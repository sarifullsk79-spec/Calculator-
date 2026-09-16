import math
import re
import ast
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation

# 🎨 iPhone ক্লাসিক ব্ল্যাক ব্যাকগ্রাউন্ড
Window.clearcolor = (0.0, 0.0, 0.0, 1)


class RoundedThemeButton(Button):

    def __init__(self, bg_color, text_color=(1, 1, 1, 1), font_size=24, radius=[dp(30)], **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.font_size = dp(font_size)
        self.bold = True

        self.custom_bg_color = bg_color
        self.custom_radius = radius

        with self.canvas.before:
            self.color_inst = Color(*self.custom_bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.custom_radius)

        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_press(self):
        super().on_press()  # 👈 কিভির ডিফল্ট বাটন প্রেস বিহেভিয়ার ঠিক রাখার জন্য
        self.color_inst.rgba = (
            min(self.custom_bg_color[0] + 0.15, 1),
            min(self.custom_bg_color[1] + 0.15, 1),
            min(self.custom_bg_color[2] + 0.15, 1),
            1
        )

    def on_release(self, *args):
        self.color_inst.rgba = self.custom_bg_color


class ExpandableCalculatorApp(App):

    def build(self):
        self.is_expanded = False
        self.is_deg = True  
        self.is_inv = False 
        self.just_calculated = False 

        main = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(18), dp(18), dp(18)],
            spacing=dp(12)
        )

        # ডিসপ্লে প্যানেল
        display_layout = BoxLayout(orientation="vertical", size_hint_y=0.28, spacing=dp(5))
        
        self.expr_input = TextInput(
            text="",
            font_size=dp(38),
            foreground_color=(0.85, 0.85, 0.85, 1),
            background_color=(0, 0, 0, 0),
            cursor_color=(1.0, 0.62, 0.04, 1),
            halign="right",
            multiline=False,
            readonly=True,  # 👈 ফোনের কিবোর্ড এড়াতে শুধুমাত্র ক্যালকুলেটর বাটন ব্যবহারের জন্য ডিজাইন করা
            cursor_width=dp(3)
        )

        self.result_label = Label(
            text="0",
            font_size=dp(48),
            color=(1.0, 0.62, 0.04, 1),
            halign="right",
            valign="top",
            bold=True
        )
        self.result_label.bind(size=self.update_label)

        display_layout.add_widget(self.expr_input)
        display_layout.add_widget(self.result_label)
        main.add_widget(display_layout)

        # 🎨 থিম কালার কম্বিনেশন
        NUM_BG = (0.20, 0.20, 0.20, 1)         
        TOP_FUNC_BG = (0.65, 0.65, 0.65, 1)    
        OPERATOR_BG = (1.0, 0.62, 0.04, 1)     
        
        TXT_WHITE = (1, 1, 1, 1)
        TXT_BLACK = (0, 0, 0, 1)

        # সায়েন্টিফিক ড্রয়ার
        self.sci_grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=0)
        self.sci_grid.opacity = 0

        sci_buttons = [
            ("√", TOP_FUNC_BG), ("π", TOP_FUNC_BG), ("^", TOP_FUNC_BG), ("!", TOP_FUNC_BG),
            ("Deg", TOP_FUNC_BG), ("sin", TOP_FUNC_BG), ("cos", TOP_FUNC_BG), ("tan", TOP_FUNC_BG),
            ("Inv", TOP_FUNC_BG), ("e", TOP_FUNC_BG), ("ln", TOP_FUNC_BG), ("log", TOP_FUNC_BG)
        ]

        self.sci_btn_objects = {}
        for text, bg in sci_buttons:
            btn = RoundedThemeButton(text=text, bg_color=bg, text_color=TXT_BLACK, font_size=20)
            btn.bind(on_release=self.button_press)
            self.sci_grid.add_widget(btn)
            if text in ["sin", "cos", "tan"]:
                self.sci_btn_objects[text] = btn
            elif text == "Inv":
                self.inv_btn = btn

        main.add_widget(self.sci_grid)

        # মেইন কিপ্যাড
        main_grid = GridLayout(cols=4, spacing=dp(10), size_hint_y=0.58)

        rows = [
            [("AC", TOP_FUNC_BG, TXT_BLACK), ("()", TOP_FUNC_BG, TXT_BLACK), ("%", TOP_FUNC_BG, TXT_BLACK), ("÷", OPERATOR_BG, TXT_WHITE)],
            [("7", NUM_BG, TXT_WHITE),       ("8", NUM_BG, TXT_WHITE),       ("9", NUM_BG, TXT_WHITE),       ("×", OPERATOR_BG, TXT_WHITE)],
            [("4", NUM_BG, TXT_WHITE),       ("5", NUM_BG, TXT_WHITE),       ("6", NUM_BG, TXT_WHITE),       ("-", OPERATOR_BG, TXT_WHITE)],
            [("1", NUM_BG, TXT_WHITE),       ("2", NUM_BG, TXT_WHITE),       ("3", NUM_BG, TXT_WHITE),       ("+", OPERATOR_BG, TXT_WHITE)],
            [("0", NUM_BG, TXT_WHITE),       (".", NUM_BG, TXT_WHITE),       ("DEL", TOP_FUNC_BG, TXT_BLACK), ("=", OPERATOR_BG, TXT_WHITE)]
        ]

        for row in rows:
            for text, bg, txt_col in row:
                font_sz = 20 if text == "DEL" else 24
                btn = RoundedThemeButton(text=text, bg_color=bg, text_color=txt_col, font_size=font_sz)
                btn.bind(on_release=self.button_press)
                main_grid.add_widget(btn)

        main.add_widget(main_grid)

        self.toggle_btn = Button(
            text="^",
            font_size=dp(32),
            size_hint=(1, None),
            height=dp(35),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1.0, 0.62, 0.04, 1),
            bold=True
        )
        self.toggle_btn.bind(on_release=self.toggle_scientific)
        main.add_widget(self.toggle_btn)

        return main

    def update_label(self, instance, value):
        instance.text_size = value

    def format_with_commas(self, number_str):
        try:
            if 'e' in number_str.lower():
                val = float(number_str)
                return f"{val:,.8g}"
            
            val_float = float(number_str)
            if abs(val_float) >= 1e15 or (0 < abs(val_float) < 1e-6):
                return f"{val_float:.8e}"
            
            is_negative = number_str.startswith('-')
            clean_str = number_str[1:] if is_negative else number_str

            if '.' in clean_str:
                parts = clean_str.split('.')
                int_part = int(parts[0])
                formatted_int = f"{int_part:,}"
                res = f"{formatted_int}.{parts[1]}"
            else:
                int_part = int(clean_str)
                res = f"{int_part:,}"

            return f"-{res}" if is_negative else res
        except (ValueError, OverflowError):
            return number_str

    def toggle_scientific(self, instance):
        if self.is_expanded:
            anim = Animation(height=0, opacity=0, duration=0.25, transition='out_quad')
            anim.start(self.sci_grid)
            self.toggle_btn.text = "^"
            self.is_expanded = False
        else:
            anim = Animation(height=dp(210), opacity=1, duration=0.25, transition='out_quad')
            anim.start(self.sci_grid)
            self.toggle_btn.text = "v"
            self.is_expanded = True

    def safe_ast_eval(self, node, eval_dict):
        if isinstance(node, ast.Expression):
            return self.safe_ast_eval(node.body, eval_dict)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ValueError("Booleans not allowed")
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported constant")
        elif isinstance(node, ast.Num):
            if isinstance(node.n, bool):
                raise ValueError("Booleans not allowed")
            if isinstance(node.n, (int, float)):
                return node.n
            raise ValueError("Unsupported number format")
        elif isinstance(node, ast.BinOp):
            left = self.safe_ast_eval(node.left, eval_dict)
            right = self.safe_ast_eval(node.right, eval_dict)
            if isinstance(node.op, ast.Add): return left + right
            elif isinstance(node.op, ast.Sub): return left - right
            elif isinstance(node.op, ast.Mult): return left * right  
            elif isinstance(node.op, ast.Div):
                if right == 0: raise ZeroDivisionError
                return left / right
            elif isinstance(node.op, ast.Pow):
                if abs(right) > 100 or abs(left) > 1e6:
                    raise OverflowError
                try:
                    res = left ** right
                except Exception:
                    raise OverflowError

                if isinstance(res, complex) or math.isinf(res) or math.isnan(res):
                    raise OverflowError
                return res
            else: raise ValueError("Unsupported operator")
        elif isinstance(node, ast.UnaryOp):
            operand = self.safe_ast_eval(node.operand, eval_dict)
            if isinstance(node.op, ast.UAdd): return +operand
            elif isinstance(node.op, ast.USub): return -operand
            else: raise ValueError("Unsupported unary operator")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in eval_dict:
                    args = [self.safe_ast_eval(arg, eval_dict) for arg in node.args]
                    return eval_dict[func_name](*args)
            raise ValueError("Unsupported function call")
        elif isinstance(node, ast.Name):
            if node.id in eval_dict:
                val = eval_dict[node.id]
                return val() if callable(val) else val
            raise ValueError("Unsupported variable")
        else:
            raise ValueError("Unsupported expression structure")

    def calculate_expression(self, current_text):
        if not current_text:
            return "0"
        
        has_operator = any(op in current_text for op in ['+', '-', '×', '÷', '%', '^', '√', '(', ')', '!', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'ln', 'π', 'e'])
        if not has_operator:
            return ""

        try:
            expr = current_text.replace("×", "*").replace("÷", "/")
            expr = expr.replace("π", "pi").replace("^", "**")
            expr = expr.replace("√", "sqrt")

            expr = re.sub(r'([0-9.]+)\s*([\+\-])\s*([0-9.]+)\s*%', r'\1 \2 (\1 * \3 / 100)', expr)
            expr = re.sub(r'([0-9.]+)\s*([\*\/])\s*([0-9.]+)\s*%', r'\1 \2 (\3 / 100)', expr)
            expr = re.sub(r'([0-9.]+)\s*%', r'(\1/100)', expr)

            while '!' in expr:
                idx = expr.find('!')
                i = idx - 1
                if i < 0:
                    break
                if expr[i] == ')':
                    depth = 1
                    i -= 1
                    while i >= 0 and depth > 0:
                        if expr[i] == ')':
                            depth += 1
                        elif expr[i] == '(':
                            depth -= 1
                        i -= 1
                    start_idx = i + 1
                else:
                    while i >= 0 and (expr[i].isalnum() or expr[i] == '.' or expr[i] == '_'):
                        i -= 1
                    start_idx = i + 1
                operand = expr[start_idx:idx]
                expr = expr[:start_idx] + f"factorial({operand})" + expr[idx+1:]

            expr = re.sub(r'\)\s*(?=\()', ')*', expr)
            expr = re.sub(r'(\d)\s*(?=\()', r'\1*', expr)
            expr = re.sub(r'(\))\s*(\d)', r'\1*\2', expr)
            expr = re.sub(r'(\d)\s*(pi|e)', r'\1*\2', expr)
            expr = re.sub(r'(pi|e)\s*(\d)', r'\1*\2', expr)
            expr = re.sub(r'(pi|e)\s*(?=\()', r'\1*', expr)
            expr = re.sub(r'(\d|\))\s*(sqrt|asin|acos|atan|sin|cos|tan|log|ln|pi|e)', r'\1*\2', expr)

            open_brackets = expr.count('(')
            close_brackets = expr.count(')')
            if open_brackets > close_brackets:
                expr += ')' * (open_brackets - close_brackets)

            def safe_factorial(x):
                if isinstance(x, bool):
                    raise ValueError("Error")
                if isinstance(x, int):
                    if x < 0 or x > 170:
                        raise ValueError("Error")
                    return math.factorial(x)
                elif isinstance(x, float):
                    if not x.is_integer() or x < 0 or x > 170:
                        raise ValueError("Error")
                    return math.factorial(int(x))
                else:
                    raise ValueError("Error")

            def safe_sqrt(x):
                if isinstance(x, bool) or x < 0:
                    raise ValueError("Error")
                return math.sqrt(x)

            def safe_log(x):
                if isinstance(x, bool) or x <= 0:
                    raise ValueError("Error")
                return math.log10(x)

            def safe_ln(x):
                if isinstance(x, bool) or x <= 0:
                    raise ValueError("Error")
                return math.log(x)

            def safe_sin(x):
                if isinstance(x, bool): raise ValueError("Error")
                if self.is_deg:
                    val = math.sin(math.radians(x))
                    if abs(x % 180) < 1e-12: return 0.0
                    return val
                else:
                    val = math.sin(x)
                    if abs(x % math.pi) < 1e-12: return 0.0
                    return val

            def safe_cos(x):
                if isinstance(x, bool): raise ValueError("Error")
                if self.is_deg:
                    val = math.cos(math.radians(x))
                    if abs((x - 90) % 180) < 1e-12: return 0.0
                    return val
                else:
                    val = math.cos(x)
                    if abs((x - math.pi/2) % math.pi) < 1e-12: return 0.0
                    return val

            def safe_tan(x):
                if isinstance(x, bool): raise ValueError("Error")
                if self.is_deg:
                    normalized = (x - 90) % 180
                    if abs(normalized) < 1e-7 or abs(normalized - 180) < 1e-7:
                        raise ValueError("Undefined")
                    val = math.tan(math.radians(x))
                    if abs(val) < 1e-12: return 0.0
                    return val
                else:
                    normalized = (x - math.pi/2) % math.pi
                    if abs(normalized) < 1e-7 or abs(normalized - math.pi) < 1e-7:
                        raise ValueError("Undefined")
                    val = math.tan(x)
                    if abs(val) < 1e-12: return 0.0
                    return val

            def safe_asin(x):
                if isinstance(x, bool) or not (-1 <= x <= 1):
                    raise ValueError("Error")
                return math.degrees(math.asin(x)) if self.is_deg else math.asin(x)

            def safe_acos(x):
                if isinstance(x, bool) or not (-1 <= x <= 1):
                    raise ValueError("Error")
                return math.degrees(math.acos(x)) if self.is_deg else math.acos(x)

            def safe_atan(x):
                if isinstance(x, bool): raise ValueError("Error")
                return math.degrees(math.atan(x)) if self.is_deg else math.atan(x)

            eval_dict = {
                "factorial": safe_factorial,
                "sqrt": safe_sqrt,
                "pi": math.pi,
                "e": math.e,
                "log": safe_log,
                "ln": safe_ln,
                "sin": safe_sin,
                "cos": safe_cos,
                "tan": safe_tan,
                "asin": safe_asin,
                "acos": safe_acos,
                "atan": safe_atan,
            }

            parsed_node = ast.parse(expr, mode='eval')
            result = self.safe_ast_eval(parsed_node, eval_dict)
            
            if isinstance(result, float):
                if result.is_integer() and abs(result) < 1e15:
                    result = int(result)
                else:
                    result = round(result, 12)
                    if float(result).is_integer() and abs(result) < 1e15:
                        result = int(result)
            
            return self.format_with_commas(str(result))
        except (SyntaxError, TypeError):
            return ""
        except (ZeroDivisionError, OverflowError, ValueError):
            return "Error"
        except Exception:
            return "Error"  # 👈 যেকোনো অপ্রত্যাশিত (unexpected) ত্রুটির ক্ষেত্রেও "Error" রিটার্ন করবে

    def insert_text(self, text_to_insert):
        cursor_col = self.expr_input.cursor[0]
        current_text = self.expr_input.text
        
        new_text = current_text[:cursor_col] + text_to_insert + current_text[cursor_col:]
        self.expr_input.text = new_text
        self.expr_input.cursor = (cursor_col + len(text_to_insert), 0)

    def button_press(self, instance):
        val = instance.text
        current_text = self.expr_input.text
        cursor_col = self.expr_input.cursor[0]

        if val == "AC":
            self.expr_input.text = ""
            self.result_label.text = "0"
            self.just_calculated = False
        elif val == "DEL":
            if self.just_calculated:
                self.expr_input.text = ""
                self.result_label.text = "0"
                self.just_calculated = False
                return

            if current_text and cursor_col > 0:
                functions = ["asin", "acos", "atan", "sin", "cos", "tan", "log", "ln", "√"]
                deleted = False
                
                for func in functions:
                    f_str = func + "(" if func != "√" else "√("
                    if cursor_col >= len(f_str) and current_text[cursor_col-len(f_str):cursor_col] == f_str:
                        self.expr_input.text = current_text[:cursor_col-len(f_str)] + current_text[cursor_col:]
                        self.expr_input.cursor = (cursor_col - len(f_str), 0)
                        deleted = True
                        break
                
                if not deleted:
                    self.expr_input.text = current_text[:cursor_col-1] + current_text[cursor_col:]
                    self.expr_input.cursor = (cursor_col - 1, 0)
        elif val == "()":
            if self.just_calculated:
                self.expr_input.text = ""
                self.result_label.text = "0"
                self.just_calculated = False
            current_text = self.expr_input.text
            if current_text.count("(") > current_text.count(")"):
                self.insert_text(")")
            else:
                self.insert_text("(")
        elif val in ["Deg", "Rad"]:
            self.is_deg = not self.is_deg
            instance.text = "Rad" if not self.is_deg else "Deg"
        elif val in ["Inv", "Inv*"]:
            self.is_inv = not self.is_inv
            if self.is_inv:
                self.inv_btn.text = "Inv*"
                self.inv_btn.custom_bg_color = (0.85, 0.85, 0.85, 1) 
                self.inv_btn.color_inst.rgba = self.inv_btn.custom_bg_color
                if "sin" in self.sci_btn_objects: self.sci_btn_objects["sin"].text = "asin"
                if "cos" in self.sci_btn_objects: self.sci_btn_objects["cos"].text = "acos"
                if "tan" in self.sci_btn_objects: self.sci_btn_objects["tan"].text = "atan"
            else:
                self.inv_btn.text = "Inv"
                self.inv_btn.custom_bg_color = (0.65, 0.65, 0.65, 1)
                self.inv_btn.color_inst.rgba = self.inv_btn.custom_bg_color
                if "sin" in self.sci_btn_objects: self.sci_btn_objects["sin"].text = "sin"
                if "cos" in self.sci_btn_objects: self.sci_btn_objects["cos"].text = "cos"
                if "tan" in self.sci_btn_objects: self.sci_btn_objects["tan"].text = "tan"
        elif val == "=":
            if not current_text:
                return
            has_operator = any(op in current_text for op in ['+', '-', '×', '÷', '%', '^', '√', '(', ')', '!', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'ln', 'π', 'e'])
            if not has_operator:
                return

            final_res = self.calculate_expression(current_text)
            if final_res is not None and final_res != "Error" and final_res != "":
                self.expr_input.text = final_res.replace(",", "")
                self.result_label.text = ""
                self.just_calculated = True
                self.expr_input.cursor = (len(self.expr_input.text), 0)
            else:
                self.result_label.text = "Error"
            return
        else:
            operators = ['+', '-', '×', '÷', '%', '^']
            if val in operators:
                if self.just_calculated:
                    self.just_calculated = False
                if not current_text:
                    if val == '-':
                        self.insert_text('-')
                    return
                if cursor_col > 0 and current_text[cursor_col-1] in operators:
                    self.expr_input.text = current_text[:cursor_col-1] + val + current_text[cursor_col:]
                else:
                    self.insert_text(val)

            elif val == '.':
                if self.just_calculated:
                    self.expr_input.text = "0."
                    self.result_label.text = "0"
                    self.just_calculated = False
                    self.expr_input.cursor = (2, 0)
                elif not current_text or (cursor_col > 0 and (current_text[cursor_col-1] in operators or current_text[cursor_col-1] == '(')):
                    self.insert_text("0.")
                else:
                    tokens = re.split(r'[\+\-\×\÷\%\^\(\)]', current_text)
                    if tokens and '.' in tokens[-1]:
                        return
                    self.insert_text(val)

            else:
                if self.just_calculated:
                    self.expr_input.text = ""
                    self.result_label.text = "0"
                    self.just_calculated = False

                if val in ["sin", "cos", "tan", "asin", "acos", "atan", "log", "ln"]:
                    self.insert_text(val + "(")
                elif val == "√":
                    self.insert_text("√(")
                elif val in ["Inv", "Inv*", "Deg", "Rad"]:
                    pass
                else:
                    self.insert_text(val)

        live_res = self.calculate_expression(self.expr_input.text)
        if live_res is not None and live_res != "":
            self.result_label.text = live_res
        elif not any(op in self.expr_input.text for op in ['+', '-', '×', '÷', '%', '^', '√', '(', ')', '!', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'ln', 'π', 'e']):
            self.result_label.text = "0"
        else:
            self.result_label.text = ""


if __name__ == "__main__":
    ExpandableCalculatorApp().run()
