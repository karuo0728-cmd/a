import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ====== 商品データ ======
products = [
    {
        "id": "apple",
        "name": "🍎 りんごジュース",
        "price": 120,
        "link": "https://pay.paypay.ne.jp/xxxxx",
        "dm_message": "🍎 りんごジュースを購入ありがとうございます！冷たく冷やして飲んでね！"
    },
    {
        "id": "coffee",
        "name": "☕ ホットコーヒー",
        "price": 200,
        "link": "https://pay.paypay.ne.jp/yyyyy",
        "dm_message": "☕ コーヒーを購入ありがとうございます！香りを楽しんでね！"
    },
    {
        "id": "snack",
        "name": "🍪 クッキー",
        "price": 150,
        "link": "https://pay.paypay.ne.jp/zzzzz",
        "dm_message": "🍪 クッキーを購入ありがとうございます！甘いひとときをどうぞ！"
    },
]

# ====== Embedを作る関数（デザイン改良版） ======
def make_embed():
    embed = discord.Embed(
        title="🛒 自販機メニュー",
        description="購入したい商品を選んでください！",
        color=0x00bfff
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3183/3183463.png")
    for p in products:
        embed.add_field(
            name=p["name"],
            value=f"💰 **¥{p['price']}**\n[支払いリンクはこちら]({p['link']})",
            inline=False
        )
    embed.set_footer(text="支払い後に /confirm コマンドで報告してください。")
    return embed

# ====== ボタン表示 ======
class VendingView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for p in products:
            self.add_item(Button(label=f"{p['name']} (¥{p['price']})", style=discord.ButtonStyle.primary, custom_id=p["id"]))

# ====== 起動時 ======
@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 スラッシュコマンド同期完了: {len(synced)} 件")
    except Exception as e:
        print(f"❌ 同期エラー: {e}")

# ====== /shop コマンド ======
@bot.tree.command(name="shop", description="自販機を開きます", guild=discord.Object(id=1427138891089186818))
async def shop(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_embed(), view=VendingView())

# ====== ボタンが押された時 ======
@bot.event
async def on_interaction(interaction):
    if not interaction.data:
        return
    item_id = interaction.data.get("custom_id")
    product = next((p for p in products if p["id"] == item_id), None)
    if not product:
        return

    # 選択した商品を記録
    with open("selected.json", "w", encoding="utf-8") as f:
        import json
        json.dump({"user_id": interaction.user.id, "product_id": product["id"]}, f)

    await interaction.response.send_message(
        f"{product['name']} を選びました！\n💰 価格: ¥{product['price']}\n[▶️ PayPayで支払う]({product['link']})\n\n支払いが完了したら `/confirm` を実行してください。",
        ephemeral=True
    )

# ====== /confirm コマンド ======
@bot.tree.command(name="confirm", description="支払い完了を報告して商品を受け取ります", guild=discord.Object(id=1427138891089186818))
async def confirm(interaction: discord.Interaction):
    import json
    if not os.path.exists("selected.json"):
        await interaction.response.send_message("⚠️ 購入情報が見つかりません。", ephemeral=True)
        return

    with open("selected.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("user_id") != interaction.user.id:
        await interaction.response.send_message("⚠️ あなたの購入履歴が見つかりません。", ephemeral=True)
        return

    product_id = data.get("product_id")
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        await interaction.response.send_message("⚠️ 商品情報が見つかりません。", ephemeral=True)
        return

    await interaction.response.send_message("✅ 支払いを確認しました！商品をDMで送信します。", ephemeral=True)
    try:
        await interaction.user.send(product["dm_message"])
    except:
        await interaction.response.send_message("⚠️ DMを送れませんでした。DMを開放してください。", ephemeral=True)

if __name__ == "__main__":
    bot.run("MTQyNzgxODI1MDEyODg1NTIyMA.GD7SDb.hM4XpusXhLx7HR2wKV0ci73G7w9F_EexX018BU")  # from flask import Flask, request, jsonify
import threading
import json

app = Flask(__name__)

@app.route("/paypay", methods=["POST"])
def paypay_webhook():
    data = request.get_json()
    print("💬 支払い通知を受け取りました:", data)

    # DiscordのユーザーIDと商品名を受け取る（PayPayから送られてくる想定）
    user_id = data.get("discord_user_id")
    product = data.get("product")

    # BotがDMを送る
    if user_id:
        bot.loop.create_task(send_dm(user_id, product))

    return jsonify({"status": "ok"})

async def send_dm(user_id, product):
    user = await bot.fetch_user(int(user_id))
    await user.send(f"✅ 支払い確認しました！\n🎁 商品: {product}")

# Flaskを別スレッドで起動
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    thread = threading.Thread(target=run_flask)
    thread.start()
    bot.run("MTQyNzgxODI1MDEyODg1NTIyMA.GD7SDb.hM4XpusXhLx7HR2wKV0ci73G7w9F_EexX018BU")

