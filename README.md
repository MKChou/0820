# ASR 語音轉文字 / TTS 文字轉語音

兩個資料夾各自獨立，進去後執行 `test.py` 即可。

```
ASR/test.py   語音 → 文字
TTS/test.py   文字 → 語音
```

## 第一次（整個專案裝一次套件）

```bat
py -3 -m pip install -r requirements.txt
```

也可以只進該資料夾裝：

```bat
cd ASR
py -3 -m pip install -r requirements.txt
```

## ASR

```bat
cd ASR
py -3 test.py
```

1. 按下 **Enter** 開始錄音  
2. 再說一次 **Enter** 停止錄音  
3. 程式會把語音送到學校伺服器，並印出文字  

音檔會存在 `ASR/recording.wav`。

## TTS

```bat
cd TTS
py -3 test.py
```

1. 在終端機輸入文字  
2. 按下 **Enter**  
3. 產生 `TTS/output.mp3` 並用系統播放器播放  

## 注意

- 需要 Python 3.9 以上，安裝時勾選 Add to PATH  
- ASR 要能連 `http://140.116.245.149:5002/proxy`（校外可能連不到）  
- TTS 需要能連 Google  
- Windows 也可在該資料夾雙擊 `run.bat`（會先裝套件再跑 `test.py`）
