/* GTK title transitions for Waybar's CFFI ABI v2.
 * ABI reference: Alexays/Waybar, resources/custom_modules/cffi_example/
 * Keep hyprland/window as the event-driven data source; no extra IPC or polling.
 */
#include <gtk/gtk.h>

typedef struct wbcffi_module wbcffi_module;
typedef struct {
    wbcffi_module *obj;
    const char *waybar_version;
    GtkContainer *(*get_root_widget)(wbcffi_module *obj);
    void (*queue_update)(wbcffi_module *obj);
} wbcffi_init_info;
typedef struct {
    const char *key;
    const char *value;
} wbcffi_config_entry;

const size_t wbcffi_version = 2;

typedef struct {
    GtkWidget *root;
    GtkWidget *revealer;
    GtkWidget *stack;
    GtkWidget *labels[2];
    GtkWidget *native_event;
    GtkLabel *source;
    char *last_title;
    guint attach_idle;
    gulong changed_handler;
} Title;

static GtkWidget *find_widget(GtkWidget *widget, gboolean find_label) {
    if (find_label ? GTK_IS_LABEL(widget)
                   : g_strcmp0(gtk_widget_get_name(widget), "window") == 0)
        return widget;

    if (!GTK_IS_CONTAINER(widget))
        return NULL;
    GList *children = gtk_container_get_children(GTK_CONTAINER(widget));
    GtkWidget *found = NULL;
    for (GList *child = children; child && !found; child = child->next)
        found = find_widget(GTK_WIDGET(child->data), find_label);
    g_list_free(children);
    return found;
}

static void sync_title(Title *self) {
    const char *title = gtk_label_get_text(self->source);
    if (g_strcmp0(title, self->last_title) == 0)
        return;
    g_free(self->last_title);
    self->last_title = g_strdup(title);

    GtkStyleContext *style = gtk_widget_get_style_context(self->revealer);
    if (!title || !*title) {
        /* Retain the outgoing title until its whole pill has faded away. */
        gtk_style_context_add_class(style, "empty");
        gtk_revealer_set_reveal_child(GTK_REVEALER(self->revealer), FALSE);
        gtk_widget_set_tooltip_text(self->root, NULL);
        return;
    }

    GtkWidget *current = gtk_stack_get_visible_child(GTK_STACK(self->stack));
    GtkWidget *next = current == self->labels[0] ? self->labels[1] : self->labels[0];
    gtk_label_set_text(GTK_LABEL(next), title);
    gtk_stack_set_visible_child(GTK_STACK(self->stack), next);
    gtk_widget_set_tooltip_text(self->root, title);
    gtk_style_context_remove_class(style, "empty");
    gtk_revealer_set_reveal_child(GTK_REVEALER(self->revealer), TRUE);
}

static void title_changed(GObject *source, GParamSpec *property, gpointer data) {
    (void)source;
    (void)property;
    sync_title(data);
}

static gboolean attach_source(gpointer data) {
    Title *self = data;
    self->attach_idle = 0;
    /* All modules have been parented into this bar by the first GTK idle. */
    GtkWidget *native = find_widget(gtk_widget_get_toplevel(self->root), FALSE);
    GtkWidget *label = native ? find_widget(native, TRUE) : NULL;
    GtkWidget *event = native ? gtk_widget_get_parent(native) : NULL;
    if (!label || !GTK_IS_EVENT_BOX(event)) {
        g_warning("window-title: cannot find hyprland/window; keeping its standard display");
        return G_SOURCE_REMOVE;
    }

    self->source = g_object_ref(GTK_LABEL(label));
    self->native_event = g_object_ref(event);
    for (unsigned i = 0; i < 2; ++i)
        gtk_label_set_max_width_chars(GTK_LABEL(self->labels[i]),
                                      gtk_label_get_max_width_chars(self->source));

    self->changed_handler = g_signal_connect(self->source, "notify::label",
                                             G_CALLBACK(title_changed), self);
    /* Hide the data source's wrapper, which native title updates never show. */
    gtk_widget_set_no_show_all(event, TRUE);
    gtk_widget_hide(event);
    sync_title(self);
    return G_SOURCE_REMOVE;
}

void *wbcffi_init(const wbcffi_init_info *info, const wbcffi_config_entry *entries,
                  size_t count) {
    (void)entries;
    (void)count;
    Title *self = g_new0(Title, 1);
    self->root = GTK_WIDGET(info->get_root_widget(info->obj));
    self->revealer = g_object_ref_sink(gtk_revealer_new());
    gtk_widget_set_name(self->revealer, "window-title-container");
    gtk_style_context_add_class(gtk_widget_get_style_context(self->revealer), "empty");
    gtk_revealer_set_transition_type(GTK_REVEALER(self->revealer),
                                     GTK_REVEALER_TRANSITION_TYPE_SLIDE_RIGHT);
    gtk_revealer_set_transition_duration(GTK_REVEALER(self->revealer), 240);

    GtkWidget *pill = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    gtk_widget_set_name(pill, "window-title");
    gtk_container_add(GTK_CONTAINER(self->revealer), pill);
    self->stack = gtk_stack_new();
    gtk_stack_set_hhomogeneous(GTK_STACK(self->stack), FALSE);
    gtk_stack_set_vhomogeneous(GTK_STACK(self->stack), TRUE);
    gtk_stack_set_interpolate_size(GTK_STACK(self->stack), TRUE);
    gtk_stack_set_transition_type(GTK_STACK(self->stack), GTK_STACK_TRANSITION_TYPE_CROSSFADE);
    gtk_stack_set_transition_duration(GTK_STACK(self->stack), 220);
    gtk_container_add(GTK_CONTAINER(pill), self->stack);

    for (unsigned i = 0; i < 2; ++i) {
        self->labels[i] = gtk_label_new("");
        gtk_label_set_single_line_mode(GTK_LABEL(self->labels[i]), TRUE);
        gtk_label_set_ellipsize(GTK_LABEL(self->labels[i]), PANGO_ELLIPSIZE_END);
        gtk_label_set_max_width_chars(GTK_LABEL(self->labels[i]), 50);
        gtk_stack_add_named(GTK_STACK(self->stack), self->labels[i], i ? "b" : "a");
    }
    gtk_container_add(GTK_CONTAINER(self->root), self->revealer);
    gtk_widget_show_all(self->revealer);
    self->attach_idle = g_idle_add_full(G_PRIORITY_HIGH_IDLE, attach_source, self, NULL);
    return self;
}

void wbcffi_update(void *instance) {
    (void)instance; /* notify::label drives updates directly on GTK's UI thread. */
}

void wbcffi_deinit(void *instance) {
    Title *self = instance;
    if (self->attach_idle)
        g_source_remove(self->attach_idle);
    if (self->source) {
        g_signal_handler_disconnect(self->source, self->changed_handler);
        g_object_unref(self->source);
        g_object_unref(self->native_event);
    }
    gtk_widget_destroy(self->revealer);
    g_object_unref(self->revealer);
    g_free(self->last_title);
    g_free(self);
}
