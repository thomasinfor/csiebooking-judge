# non-official judge for csiebooking

大家如果寫完SP的話可以測測看非官方的judge：
1. ssh 進 linux1.csie.org ~ linux15.csie.org ***現在1\~15都可以用了！！！***
2. cd 到你 Makefile 所在的資料夾
3. 執行 `/tmp2/b10902028/SP-judge/submit.py --name [NAME] -a --teacher tw`
其中 `[NAME]` 可以是任意大小寫英文+數字+底線組成的字串，是用來辨別你的身分的
4. 等待它執行完畢就會輸出結果（可能需要數分鐘）

結果會分成計分板以及你 server 錯誤的行為

計分板每個 task 中的每一列代表輸出跟你一樣的人，第一列（最多人相同的那列）通常是正解

judge 最後會輸出你跟正解的差異，灰色是你 server 的行為，綠色是第一個產生差異的地方正解的行為。`<<` 代表 client 傳給 server 的東西，`>>` 代表 server 傳給 client 的東西。剩下就靠大家自己通靈 XD

然後如果錯誤是出現在 judge 認為你的 server 沒有輸出東西的話 有一定的可能是工作站網路被塞爆所以跑很慢 你可以執行時加上 `--time ???` 把時限調整成 `???` 秒

如果只是想看計分板可以打 `/tmp2/b10902028/SP-judge/submit.py --name [NAME] --sum`

既然這是非官方的 judge，如果結果有誤絕對不要怪我：( 但他可信度應該蠻高的