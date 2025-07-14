import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import time


def visualize_realtime(city_file, tour_file_to_watch):
    """
    TSPの経路をリアルタイムで可視化する関数
    """
    # --- 初期設定 ---
    plt.ion()  # インタラクティブモードをオン
    fig, ax = plt.subplots(figsize=(10, 10))
    last_update_time = 0

    # 都市データを最初に一度だけ読み込む
    try:
        cities = pd.read_csv(city_file)
        cities.columns = ["x", "y"]
    except FileNotFoundError:
        print(f"エラー: 都市ファイル '{city_file}' が見つかりません。")
        return

    print(
        f"'{tour_file_to_watch}' を監視しています... (プロットウィンドウを閉じると終了します)"
    )

    # --- メインループ ---
    while plt.fignum_exists(fig.number):  # ウィンドウが開いている間ループ
        try:
            # 監視対象ファイルの最終更新時刻をチェック
            if os.path.exists(tour_file_to_watch):
                current_update_time = os.path.getmtime(tour_file_to_watch)

                # ファイルが更新されていたら再描画
                if current_update_time > last_update_time:
                    last_update_time = current_update_time

                    # 少し待って書き込み完了を確認
                    time.sleep(0.1)

                    # 経路データを読み込む
                    tour_df = pd.read_csv(tour_file_to_watch, header=0)

                    # 'index' 行をスキップして都市番号だけ取得
                    tour_indices = tour_df.iloc[:, 0].astype(int).tolist()

                    # 最後の都市が最初の都市と同じ場合（循環）は除去
                    if len(tour_indices) > 1 and tour_indices[-1] == tour_indices[0]:
                        tour_indices = tour_indices[:-1]

                    # 都市順に並べ替え
                    ordered_cities = cities.iloc[tour_indices]

                    # 循環経路のため最初の都市を最後に追加
                    tour_path = pd.concat(
                        [ordered_cities, ordered_cities.iloc[:1]], ignore_index=True
                    )

                    # 現在の総距離を計算
                    dist = (tour_path.diff().pow(2).sum(axis=1).pow(0.5)).sum()

                    # --- 描画処理 ---
                    ax.clear()  # 前の描画をクリア

                    # 経路を描画
                    ax.plot(
                        tour_path["x"],
                        tour_path["y"],
                        color="red",
                        linestyle="-",
                        linewidth=1.0,
                        zorder=1,
                    )

                    # 都市の点を描画
                    ax.scatter(
                        cities["x"], cities["y"], color="skyblue", s=10, zorder=2
                    )

                    # 装飾
                    ax.set_title(
                        f"TSP Real-time Visualization ({len(cities)} Cities)\nDistance: {dist:.2f}"
                    )
                    ax.set_aspect("equal", adjustable="box")
                    ax.grid(True)

                    # 強制的に描画更新
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    plt.pause(0.001)  # 追加: 描画を強制的に更新

                    print(f"経路を更新しました。 Score: {dist:.2f}")

            # 0.1秒待機（より頻繁にチェック）
            time.sleep(0.1)

        except FileNotFoundError:
            # ソルバーがまだファイルを作成していない場合
            ax.clear()
            ax.set_title("Waiting for solver to start...")
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(1)
        except Exception as e:
            # 読み込み中のエラーなどを表示
            print(f"描画エラー: {e}")
            time.sleep(0.5)

    print("ビジュアライザを終了しました。")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python visualizer.py <city_file.csv> <tour_file_to_watch.csv>")
        print("例: python visualizer.py input_5.csv realtime_tour.csv")
    else:
        visualize_realtime(sys.argv[1], sys.argv[2])
