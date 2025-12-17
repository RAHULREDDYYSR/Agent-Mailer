import gradio as gr

# Clean, standard CSS adjustments
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body, .gradio-container, .prose {
    font-family: 'Inter', sans-serif !important;
}

/* Make inputs look a bit cleaner */
textarea, input {
    border-radius: 6px !important;
    border: 1px solid var(--border-color-primary) !important;
}

/* Button polishing */
button.primary {
    font-weight: 600 !important;
}

/* Header styling */
.main-header {
    text-align: center;
    margin-bottom: 1rem;
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
}
"""

def get_theme():
    """Returns a standard Soft theme."""
    return gr.themes.Soft(
        primary_hue="indigo",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
    )
