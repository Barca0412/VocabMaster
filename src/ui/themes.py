"""
Theme definitions inspired by Claude's minimalist aesthetic
"""

LIGHT_THEME = {
    "name": "light",
    
    # Background colors
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F7F7F5",
    "bg_tertiary": "#EEEEEC",
    
    # Text colors
    "text_primary": "#1E1E1E",
    "text_secondary": "#666666",
    "text_tertiary": "#999999",
    
    # Accent colors
    "accent": "#D97706",
    "accent_hover": "#B45309",
    "accent_light": "#FEF3C7",
    
    # Border colors
    "border": "#E5E5E5",
    "border_focus": "#D97706",
    
    # Status colors
    "success": "#059669",
    "error": "#DC2626",
    "warning": "#F59E0B",
    
    # Button colors
    "button_bg": "#F5F5F4",
    "button_hover": "#E7E5E4",
    "button_active": "#D6D3D1",
    "button_text": "#1E1E1E",
}

DARK_THEME = {
    "name": "dark",
    
    # Background colors
    "bg_primary": "#1A1A1A",
    "bg_secondary": "#252525",
    "bg_tertiary": "#2F2F2F",
    
    # Text colors
    "text_primary": "#ECECEC",
    "text_secondary": "#B4B4B4",
    "text_tertiary": "#8A8A8A",
    
    # Accent colors
    "accent": "#F59E0B",
    "accent_hover": "#FBBF24",
    "accent_light": "#451A03",
    
    # Border colors
    "border": "#3A3A3A",
    "border_focus": "#F59E0B",
    
    # Status colors
    "success": "#10B981",
    "error": "#EF4444",
    "warning": "#F59E0B",
    
    # Button colors
    "button_bg": "#2F2F2F",
    "button_hover": "#3A3A3A",
    "button_active": "#454545",
    "button_text": "#ECECEC",
}


def get_stylesheet(theme: dict) -> str:
    """Generate Qt stylesheet from theme dictionary"""
    return f"""
        QMainWindow, QWidget {{
            background-color: {theme['bg_primary']};
            color: {theme['text_primary']};
        }}
        
        QLabel {{
            color: {theme['text_primary']};
            background-color: transparent;
        }}
        
        QFrame#bottomNavbar {{
            background-color: {theme['bg_secondary']};
            border-top: 1px solid {theme['border']};
            border-radius: 0;
        }}
        
        QPushButton#navbarButton {{
            background-color: transparent;
            color: {theme['text_secondary']};
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 500;
            min-height: 32px;
        }}
        
        QPushButton#navbarButton:hover {{
            background-color: {theme['button_hover']};
            color: {theme['text_primary']};
        }}
        
        QPushButton#navbarButton:pressed {{
            background-color: {theme['button_active']};
        }}
        
        QLabel#wordLabel {{
            font-size: 32px;
            font-weight: 500;
            color: {theme['text_primary']};
        }}
        
        QLabel#phoneticLabel {{
            font-size: 16px;
            color: {theme['text_secondary']};
        }}
        
        QLabel#definitionLabel {{
            font-size: 14px;
            color: {theme['text_primary']};
            line-height: 1.6;
        }}
        
        QLabel#translationLabel {{
            font-size: 14px;
            color: {theme['text_secondary']};
        }}
        
        QLabel#exampleLabel {{
            font-size: 13px;
            color: {theme['text_tertiary']};
            font-style: italic;
        }}
        
        QPushButton {{
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['button_hover']};
            border-color: {theme['border_focus']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['button_active']};
        }}
        
        QPushButton#accentButton {{
            background-color: {theme['accent']};
            color: white;
            border: none;
        }}
        
        QPushButton#accentButton:hover {{
            background-color: {theme['accent_hover']};
        }}
        
        QLineEdit, QTextEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {theme['border_focus']};
            outline: none;
        }}
        
        QComboBox {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
        }}
        
        QComboBox:hover {{
            border-color: {theme['border_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent_light']};
        }}
        
        QCheckBox {{
            color: {theme['text_primary']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {theme['border']};
            border-radius: 4px;
            background-color: {theme['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme['accent']};
            border-color: {theme['accent']};
        }}
        
        QScrollArea {{
            border: none;
            background-color: {theme['bg_primary']};
        }}
        
        QScrollBar:vertical {{
            background-color: {theme['bg_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['border']};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['text_tertiary']};
        }}
        
        QDialog {{
            background-color: {theme['bg_primary']};
        }}
    """


def get_theme(theme_name: str) -> dict:
    """Get theme by name"""
    if theme_name.lower() == "dark":
        return DARK_THEME
    return LIGHT_THEME
