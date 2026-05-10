# KivyMD compatibility shim
from kivy.factory import Factory
from kivymd import __version__ as kivymd_version

# Check KivyMD version
is_kivymd_2 = kivymd_version.startswith('2.')

if is_kivymd_2:
    print("[COMPAT] Detected KivyMD 2.0 - Applying compatibility patches...")
    
    from kivymd.uix.label import MDLabel
    from kivymd.theming import ThemeManager
    from kivy.properties import OptionProperty
    
    # KivyMD 1.2.0 to 2.0 font style mapping
    font_style_map = {
        'H1': 'display-large',
        'H2': 'display-medium',
        'H3': 'display-small',
        'H4': 'headline-large',
        'H5': 'headline-medium',
        'H6': 'headline-small',
        'Subtitle1': 'title-medium',
        'Subtitle2': 'title-small',
        'Body1': 'body-large',
        'Body2': 'body-medium',
        'Button': 'label-large',
        'Caption': 'label-small',
        'Overline': 'label-small',
        'Icon': 'label-large',
    }
    
    # Patch ThemeManager to add old font styles
    original_theme_init = ThemeManager.__init__
    
    def patched_theme_init(self, **kwargs):
        original_theme_init(self, **kwargs)
        # Add KivyMD 1.2.0 font styles as aliases
        for old_style, new_style in font_style_map.items():
            if new_style in self.font_styles and old_style not in self.font_styles:
                self.font_styles[old_style] = self.font_styles[new_style]
    
    ThemeManager.__init__ = patched_theme_init
    
    # Patch MDLabel to convert old font styles to new ones
    original_label_init = MDLabel.__init__
    
    def patched_label_init(self, **kwargs):
        if 'font_style' in kwargs and kwargs['font_style'] in font_style_map:
            kwargs['font_style'] = font_style_map[kwargs['font_style']]
        original_label_init(self, **kwargs)
    
    MDLabel.__init__ = patched_label_init
    
    print("[COMPAT] Font style compatibility enabled")

try:
    from kivymd.uix.button import MDRaisedButton
except ImportError:
    from kivymd.uix.button import MDButton
    
    class MDRaisedButton(MDButton):
        def __init__(self, **kwargs):
            kwargs.setdefault('style', 'elevated')
            super().__init__(**kwargs)

try:
    from kivymd.uix.tab import MDTabs
except ImportError:
    from kivymd.uix.navigationbar import MDNavigationBar
    MDTabs = MDNavigationBar

Factory.register('MDRaisedButton', cls=MDRaisedButton)
Factory.register('MDTabs', cls=MDTabs)
