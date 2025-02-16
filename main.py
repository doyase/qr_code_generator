from flask import Flask, render_template, request, send_file
import qrcode
import io
import base64
import os

app = Flask(__name__)

# 一時保存用のQRコードファイルパス
TEMP_FILE_PATH = "static/qr_code.png"

def generate_qr(data):
    """QRコードを生成し、Base64形式で返す"""
    if not data:
        return None, "⚠️ 入力が空です。QRコードを生成できません。"

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # `static` フォルダを作成して画像を保存
        os.makedirs("static", exist_ok=True)
        img.save(TEMP_FILE_PATH, format="PNG")

        # Base64エンコードしてHTMLで表示
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

        return img_base64, None

    except Exception as e:
        return None, f"⚠️ QRコード生成エラー: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    qr_image = None
    error_message = None

    if request.method == "POST":
        data = request.form.get("qr_data", "").strip()
        qr_image, error_message = generate_qr(data)

    return render_template("index.html", qr_code=qr_image, error=error_message)

@app.route("/download")
def download_qr():
    """QRコードをダウンロード"""
    if os.path.exists(TEMP_FILE_PATH):
        return send_file(TEMP_FILE_PATH, mimetype="image/png", as_attachment=True, download_name="qr_code.png")
    
    return "⚠️ QRコードが生成されていません。", 400

if __name__ == "__main__":
    app.run(debug=True)
