import cv2
import numpy as np
import pandas as pd

# 設定エリア
CSV_PATH = "data.csv"
IMG_PATH = "kuwagata_all.jpg"

# 1. データの読み込み
df = pd.read_csv(CSV_PATH)

# 初回実行時、CSVにH, S, V列がない場合は作成しておく
if "H" not in df.columns:
    df["H"] = np.nan
    df["S"] = np.nan
    df["V"] = np.nan

# 画像の読み込み
img = cv2.imread(IMG_PATH)
if img is None:
    print(f"エラー: 画像 '{IMG_PATH}' が読み込めませんでした。")
    exit()

# OpenCVのデフォルト(BGR)からHSVに変換
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# クリックした座標を保存するリスト
points = []


# マウスクリック時のコールバック関数
def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 3:
            points.append((x, y))


print("=== 抽出開始 ===")
print("【操作方法】")
print("  ・3点クリック: 範囲の指定")
print("  ・[Z] キー: 1つ前のクリックを取り消す (Undo)")
print("  ・[R] キー: その個体のクリックをすべてやり直す (Reset)")
print("  ・[Enter] または [N] キー: 3点揃ったら確定して次の個体へ (Next)")
print(
    "  ※途中でやめる場合は [Esc] キーを押すと保存して安全に中断します。次回は未処理から再開します。"
)
print("=================")

# 自由にリサイズできるウィンドウを作成
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1200, 800)
# マウスイベントの登録
cv2.setMouseCallback("Image", click_event)

for index, row in df.iterrows():
    if pd.notna(df.at[index, "H"]):
        print(
            f"[{index + 1}/{len(df)}] 個体ID: {row['ID']} は処理済みのため次へ進みます。"
        )
        continue

    points = []  # 個体ごとにリセット

    print(
        f"\n[{index + 1}/{len(df)}] 個体ID: {row['ID']} の部位を3点クリックしてください..."
    )

    # ユーザーが確定するまでループ
    while True:
        img_disp = img.copy()

        # 現在クリックされている点と線を描画
        for pt in points:
            cv2.circle(img_disp, pt, 10, (0, 0, 255), -1)

        # 3点揃ったら緑の三角形を描画
        if len(points) == 3:
            pts = np.array(points, np.int32)
            cv2.polylines(
                img_disp, [pts], isClosed=True, color=(0, 255, 0), thickness=5
            )

        cv2.imshow("Image", img_disp)

        # キー入力を待機（20ミリ秒ごとに更新）
        key = cv2.waitKey(20) & 0xFF

        # [Z] キー：1つ消す
        if key == ord("z") or key == ord("Z"):
            if len(points) > 0:
                points.pop()
                print("  -> 直前のポイントを取り消しました。")

        # [R] キー：すべてリセット
        elif key == ord("r") or key == ord("R"):
            points.clear()
            print("  -> ポイントをリセットしました。最初からクリックしてください。")

        # [Enter] (13) または [N] キー：次へ進む
        elif key == 13 or key == ord("n") or key == ord("N"):
            if len(points) == 3:
                break  # ループを抜けてHSV計算へ
            else:
                print(
                    "  ⚠️ まだ3点選択されていません。確定するには3点クリックしてください。"
                )

        # [Esc] (27) キー：強制終了（安全にスクリプトを止める用）
        elif key == 27:
            print("\n=== Escキーが押されたため、処理を中断します ===")
            cv2.destroyAllWindows()
            exit()

    # --- ループを抜けた後の処理（HSV計算とCSVへの直接保存） ---
    # 三角形のマスク（抽出範囲）を作成
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    pts = np.array(points, np.int32)
    cv2.fillPoly(mask, [pts], 255)

    # マスク内の平均HSVを計算
    mean_hsv = cv2.mean(hsv_img, mask=mask)

    # DataFrameの現在の行（index）に数値を直接書き込む
    df.at[index, "H"] = mean_hsv[0]
    df.at[index, "S"] = mean_hsv[1]
    df.at[index, "V"] = mean_hsv[2]

    print(f"  成功 -> H:{mean_hsv[0]:.1f}, S:{mean_hsv[1]:.1f}, V:{mean_hsv[2]:.1f}")

    # 個体ごとにCSVを上書き保存
    df.to_csv(CSV_PATH, index=False)
    print(f"  -> {CSV_PATH} を更新しました。")

cv2.destroyAllWindows()
print("\n=== 全ての個体の処理が完了しました ===")
