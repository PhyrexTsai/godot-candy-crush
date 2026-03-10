# Project Overview

Candy Crush clone — Godot 4.6 GDScript 三消遊戲。

## 專案結構

```
candy-crush/
├── project.godot          # Godot 專案設定（gl_compatibility, 1280x720）
├── CLAUDE.md              # AI 協作指引
├── export_presets.cfg     # Web 匯出設定
├── scripts/
│   └── main.gd            # 全部遊戲邏輯（單一腳本架構）
├── scenes/
│   └── main.tscn           # 主場景，根節點為 Node2D
├── assets/
│   └── sprites/            # 預留的 sprite 資源目錄（尚未使用）
├── docs/
│   ├── web-export-guide.md # Web 匯出指南
│   └── project-overview.md # 本文件
└── export/                 # 匯出產物（已 gitignore）
```

## 核心資料結構

遊戲狀態由兩個平行的 8x8 二維陣列表示：

| 陣列 | 型別 | 內容 |
|------|------|------|
| `grid` | `Array` of `int` | 糖果類型（0–5），-1 = 空格 |
| `candy_nodes` | `Array` of `ColorRect` | 對應的視覺節點 |

**鐵律**：這兩個陣列必須始終保持同步。任何修改 `grid` 的操作，都必須同步更新 `candy_nodes`。

## 遊戲機制

### 初始化
`_init_grid()` 填充隨機糖果，`_random_candy_no_match()` 確保初始盤面不存在三連。

### 輸入處理
點擊選取 → 點擊相鄰格交換。`is_animating` 旗標在動畫期間鎖定輸入。

### 消除流程（核心迴圈）

```
swap → find_matches → process_matches ─┐
                                        ├→ remove matched
                                        ├→ apply_gravity（下落）
                                        ├→ refill（補充新糖果）
                                        └→ find_matches（連鎖檢測，遞迴）
```

- **Match detection**：水平 + 垂直掃描，run-length 演算法，≥3 連即消除
- **Gravity**：由下往上掃描每列，將非空格往下堆疊
- **Refill**：從頂部掉落新的隨機糖果
- **Chain reaction**：遞迴呼叫 `_process_matches()`

### 計分
每消除一顆糖果 +10 分。連鎖消除累加計分。

## 技術決策

### 渲染器：gl_compatibility
唯一支援 Web 匯出的渲染器。Forward+ 和 Mobile 渲染器不支援 HTML5。

### 單腳本架構
所有邏輯集中在 `scripts/main.gd`（約 320 行）。對於目前的複雜度，這是最簡單直接的做法——不需要過早拆分為多個類別。

### 程序化視覺
全部使用 `ColorRect` 節點，無外部圖片資源。6 種糖果用 6 種顏色區分。棋盤背景使用明暗交替的格子。

### 動畫系統
使用 Godot 內建 `Tween`，搭配 `await tween.finished` 實現非同步動畫流程。

## 常數

| 常數 | 值 | 說明 |
|------|-----|------|
| `GRID_SIZE` | 8 | 棋盤大小 |
| `CELL_SIZE` | 64 | 格子像素大小 |
| `CANDY_TYPES` | 6 | 糖果種類數 |
| `BOARD_OFFSET` | `(384, 104)` | 棋盤左上角位置，將 512x512 置中於 1280x720 |
| `MARGIN` | 4.0 | 糖果與格子邊緣的間距 |
