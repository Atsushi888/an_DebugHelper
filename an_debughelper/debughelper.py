# -*- coding: utf-8 -*-
"""DBHL_20250214_00.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1VaR5vnZedcO2wxFShVylkKax-qEkd77c

# DebugHelper
デバッグ作業をサポートする。


```
2025/01/18 DebugHelper2をpip化するために作成
2025/01/19 flg_debugをなくすための修正
2025/02/11 0.2.1 CheckpointManager追加
2025/02/12 0.2.2 log_step改良。実行中のクラスとメソッドを表示するようにした。
2025/02/13 0.2.3 what_do_you_do を追加。コマンドの実行を選択できるようにした。
2025/02/14 0.2.4 what_do_you_do 改良。戻り値関係。
```

# DebugHelper

## 1. 初期設定
"""

# @title a. 初期値設定{"form-width":"400px"}
# @markdown Log_folder, Log_file(デバッグログを記録)
log_folder = "/content/drive/MyDrive/log"  # @param {type:"string"}
log_file = "debug.log"  # @param {type:"string"}

# @title b. GDrive接続
from google.colab import drive
drive.mount('/content/drive')

"""## 2. モジュール定義"""

# @title a. DebugHelper_old 定義 {"form-width":"400px"}
import inspect

class DebugHelper_old:
    def __init__(self):
        self.debug = True
        self.checklist = ChecklistManager()  # チェックリスト管理
        self.step_counter = 1


    def debug_print(self, *args, end="\n"):
        """デバッグモードのときにのみメッセージを出力"""
        if self.debug:
            cls_name, method_name = self.get_current_method_info()
            message = f"[{cls_name}.{method_name}] " + " ".join(map(str, args))
            print(message, end = end )

    def enable_debug(self):
        """デバッグモードを有効にする"""
        self.debug = True

    def disable_debug(self):
        """デバッグモードを無効にする"""
        self.debug = False

    def get_current_method_info(self):
        """現在のクラス名とメソッド名を取得"""
        frame = inspect.currentframe().f_back.f_back
        method_name = frame.f_code.co_name
        cls_name = None
        if 'self' in frame.f_locals:
            cls_name = frame.f_locals['self'].__class__.__name__
        return cls_name, method_name

# @title b. DebugHelper 定義{"form-width":"400px"}
import os
import inspect
import subprocess

class DebugHelper:
    def __init__(self):
        """チェックリストを管理するクラス"""
        self.debug = True
        self.entries = []  # 記録するエントリ一覧

    def enable_debug(self):
        """デバッグモードを有効にする"""
        self.debug = True

    def disable_debug(self):
        """デバッグモードを無効にする"""
        self.debug = False

    def start_step(self, step_name):
        """チェックリストにステップ開始を記録"""
        print(f"🔹 チェック開始: {step_name}")
        self.entries.append({"ステップ": step_name, "内容": "進行中", "結果": "⚠️ 進行中"})

    def add_step(self, step_key, description):
        """
        チェックリストに手順を追加
        :param step_key: 手順の一意なキー
        :param description: 手順の説明
        """
        if step_key not in self.entries:
            self.entries.append({
                "ステップ": step_key,
                "処理内容": description,
                "結果": "未実行"
            })
        else:
            print(f"⚠️ 手順 {step_key} はすでに登録済みです。")


    def complete_step(self, step_name, success=True):
        """ステップを完了として記録"""
        for entry in self.entries:
            if entry["ステップ"] == step_name:
                entry["結果"] = "✅ 成功" if success else "❌ 失敗"
                return
        print(f"⚠️ ステップ `{step_name}` が見つかりません")




    def debug_print(self, *args, end="\n", back=0):
        """デバッグモードのときにのみメッセージを出力"""
        if self.debug:
            cls_name, method_name = self.get_current_method_info(back=back)
            message = f"[{cls_name}.{method_name}] " + " ".join(map(str, args))
            print(message, end=end)



    def log_step(self,  *args, end="\n", success=None):
        """ ステップの実行ログを記録する。"""

        # 呼び出し元のクラス・メソッド名を取得（2フレーム前を参照）
        frame = inspect.currentframe().f_back.f_back

        cls_name, method_name = self.get_current_method_info()
        # ログのヘッダーにクラス・メソッド情報を追加
        full_message = f"[{cls_name}.{method_name}] " + " ".join(map(str, args))

        if success is True:
            full_message = "✅ " + full_message
        elif success is False:
            full_message = "❌ " + full_message
        else:
            full_message = "🔹 " + full_message

        print(full_message, end = end)  # デバッグ表示



    def what_do_you_do(self, message, command):
        """
        ユーザーに対して次のアクションを選択させる。

        - self.debug が True の場合、選択肢を提示。
        - self.debug が False の場合、確認なしで即実行。

        Args:
            message (str): 実行前に表示するメッセージ
            command (str): 実行するコマンド

        Returns:
            ( stdout, stderr ): コマンドが成功した場合
            ( None, None ): コマンドが失敗した場合
        """
        if self.debug:
            self.debug_print(f"🎮説明\n{message}", back = 1 )
            self.debug_print(f"📠コマンド:\n{command}", back = 1)
            self.debug_print("1️⃣ 実行する", back = 1)
            self.debug_print("2️⃣ やめておく", back = 1)
            self.debug_print("3️⃣ コマンドを変更する", back = 1)
            choice = input("🔹 どうする？ (1/2/3): ").strip()

            if choice == "1":
                pass
            elif choice == "2":
                self.debug_print("🛑 操作をキャンセルしました。", back = 1)
                return None, None
            elif choice == "3":
                command = input("💬 新しいコマンドを入力してください: ").strip()
            else:
                self.debug_print("⚠️ 無効な選択肢です", back=1)
                return None, None

        self.debug_print(f"🚀 実行中:\n{command}", back=1)
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            self.debug_print("✅ コマンド実行完了", back=1)
            self.debug_print(f"stdout:\n{result.stdout}", back=1)
            self.debug_print(f"stderr:\n{result.stderr}", back=1)
            return result.stdout, result.stderr
        except Exception as e:
            self.debug_print(f"❌ コマンド実行中にエラー: {e}", back=1)
            return None, None



    def get_current_method_info(self, back=0):
        """現在のクラス名とメソッド名を取得（可変バックトレース対応）"""
        frame = inspect.currentframe()
        for _ in range(2 + back):  # 2は元々の f_back.f_back
            if frame is None or frame.f_back is None:
                break
            frame = frame.f_back

        method_name = frame.f_code.co_name if frame else "Unknown"
        cls_name = None
        if frame and 'self' in frame.f_locals:
            cls_name = frame.f_locals['self'].__class__.__name__

        return cls_name, method_name



    def add_entry(self, category, description, success=None):
        """カテゴリごとの処理を記録"""
        status = "✅ 成功" if success is True else "❌ 失敗" if success is False else "⚠️ 未判定"
        entry = {"カテゴリ": category, "処理内容": description, "結果": status}
        self.entries.append(entry)

    def display(self):
        """チェックリストを表示"""
        print("\n🔹 **チェックリスト** 🔹")
        for idx, entry in enumerate(self.entries, start=1):
            category = entry.get("カテゴリ", entry.get("ステップ", "不明"))
            description = entry.get("処理内容", entry.get("内容", "説明なし"))
            result = entry.get("結果", "⚠️ 未判定")
            print(f"Step {idx}: [{category}] {description} → {result}")

    def export_txt(self, filename= os.path.join( log_folder, log_file ) ):
        """チェックリストをテキストファイルに出力"""
        with open(filename, "w", encoding="utf-8") as f:
            for idx, entry in enumerate(self.entries, start=1):
                category = entry.get("カテゴリ", entry.get("ステップ", "不明"))
                description = entry.get("処理内容", entry.get("内容", "説明なし"))
                result = entry.get("結果", "⚠️ 未判定")
                f.write(f"Step {idx}: [{category}] {description} → {result}\n")
        print(f"✅ チェックリストを {filename} に保存しました。")

    def clear(self):
        """チェックリストをクリア"""
        self.entries = []
        print("✅ チェックリストをリセットしました。")



    def run_command(self, command, back = 0):
        """
        Jupyter 環境でシステムコマンドを実行し、出力をリアルタイムで表示する。

        Args:
            command (str): 実行するコマンド

        Returns:
            bool: コマンドが成功した場合 True、失敗した場合 False
        """
        self.debug_print(f"🔹 コマンド実行: {command}", back = back)

        try:
            get_ipython().system(command)  # Jupyter Notebook でコマンド実行
            self.debug_print(f"✅ コマンド成功: {command}", back = back)
            return True
        except Exception as e:
            self.debug_print(f"❌ コマンド失敗: {command}\n{str(e)}", back = back)
            return False

"""## 2. テスト"""

# @title a. テスト {"form-width":"400px"}
class TestClass:
    def __init__(self):
        self.debugger = DebugHelper()
        self.debugger.debug_print("TestClassのコンストラクタが呼ばれました。")
        self.debugger.log_step("TestClassのコンストラクタが呼ばれました。", success=True)
        self.debugger.add_entry("テストクラス", "TestClassのコンストラクタが呼ばれました。", success=True)
        self.debugger.add_step("テストクラス", "TestClassのコンストラクタが呼ばれました。")
        self.debugger.display()
        self.debugger.export_txt()
        self.debugger.clear()


    def test_method(self):
        self.debugger.add_entry("テストメソッド", "test_methodが呼ばれました。", success=True)
        self.debugger.what_do_you_do("バカめ!!!", "echo バカめバカめバカめ!!!")

if __name__ == "__main__":
    tc1 = TestClass()
    tc1.test_method()