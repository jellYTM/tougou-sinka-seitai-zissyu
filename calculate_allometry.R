data <- read.csv("data.csv")
head(data)
plot(data = data, ML ~ TL)

data_log2 <- log2(data[, -1])
head(data_log2)

cor_matrix <- cor(data_log2, use = "complete.obs")


# 回帰直線と数式を描画するカスタム関数
panel.lm.formula <- function(x, y, ...) {
  # 1. 散布図の点を描画
  points(x, y, ...) 
  
  ok <- is.finite(x) & is.finite(y)
  if (any(ok)) {
    # 2. 回帰モデルの作成と直線の描画
    model <- lm(y[ok] ~ x[ok])
    abline(model, col = "blue", lwd = 2)
    
    # 3. 傾き(a)、切片(b)、決定係数(R2)を取得して丸める
    a <- round(coef(model)[2], 3)
    b <- round(coef(model)[1], 3)
    r2 <- round(summary(model)$r.squared, 3)
    
    # 4. 数式の文字列を作成（切片がマイナスの時の見た目を整える）
    if(b >= 0) {
      eq <- sprintf("y = %.3fx + %.3f", a, b)
    } else {
      eq <- sprintf("y = %.3fx - %.3f", a, abs(b))
    }
    eq_r2 <- sprintf("R² = %.3f", r2)
    
    # 5. プロットの左上付近にテキストを表示
    usr <- par("usr") # 現在のプロット領域の座標を取得
    text(x = usr[1] + 0.05 * (usr[2] - usr[1]), # X座標 (左から5%の位置)
         y = usr[4] - 0.10 * (usr[4] - usr[3]), # Y座標 (上から10%の位置)
         labels = paste(eq, eq_r2, sep = "\n"), # 数式とR2を改行して表示
         pos = 4,         # 指定座標の右側にテキストを配置
         col = "red",     # 文字の色
         cex = 1.0)       # 文字のサイズ（はみ出る場合は0.8などに小さくしてください）
  }
}

# 実行（upper.panelは相関係数など別のものを入れたい場合は変更可能。今回は下半分に数式を表示）
pairs(data_log2, 
      lower.panel = panel.lm.formula, # 下半分は数式付き散布図
      upper.panel = NULL,             # 上半分は空白（図がごちゃごちゃするのを防ぐため）
      main = "すべての形質の散布図と回帰式", 
      pch = 16, col = rgb(0, 0, 0, 0.5))

