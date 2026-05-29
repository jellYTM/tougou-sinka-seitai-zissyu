library(ggplot2)
library(dplyr)

# 1. Pythonで出力したCSVの読み込み
data <- read.csv("data.csv")
data <- na.omit(data) # 抽出失敗（NaN）の行を削除

# 2. H, S, Vの値を使ってPCA（主成分分析）を実行
pca_result <- prcomp(data[, c("H", "S", "V")], scale. = TRUE)

# 3. 主成分スコア（PC1, PC2）をデータフレームに追加
data$PC1 <- pca_result$x[, 1]
data$PC2 <- pca_result$x[, 2]

# 4. プロット用にOpenCVのHSVスケールをR用のHexカラーコード（#RRGGBB）に変換
# OpenCV: H(0-179), S(0-255), V(0-255) -> Rのhsv関数: h(0-1), s(0-1), v(0-1)
data$Actual_Color <- hsv(h = data$H / 179, s = data$S / 255, v = data$V / 255)

# 5. PC1とPC2の値をCSVとして保存
write.csv(data, "data_ready_for_allo.csv", row.names = FALSE)

# 6. PCAの散布図プロット（点の色を実際のクワガタの色で描画）
pca_plot <- ggplot(data, aes(x = PC1, y = PC2, color = Actual_Color)) +
  geom_point(size = 4, alpha = 0.8) +
  scale_color_identity() + # 実際のカラーコードを使用
  theme_minimal() +
  labs(
    title = "HSVデータに基づくPCA散布図",
    x = "PC1",
    y = "PC2"
  )

print(pca_plot)
