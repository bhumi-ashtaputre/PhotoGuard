from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from PIL import Image
import numpy as np
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'photoguard_secret_2024')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ── In-memory store ───────────────────────────────────────────────────────────
USERS        = {}   # email -> {password, account_type, lang}
SOCIAL_LINKS = {}   # email -> {platform: handle}
TRUSTED      = {}   # email -> [friend_ids]
UPLOADS      = {}   # email -> [filenames]

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── Translations ──────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "login": "Login", "register": "Register", "email": "Email Address",
        "password": "Password", "account_type": "Account Type",
        "public": "Public", "private": "Private", "language": "Language",
        "tagline": "Your photos. Your rules.", "link_accounts": "Link Accounts",
        "trusted_friends": "Trusted Friends", "ai_detection": "AI Detection",
        "upload_photos": "Upload Photos", "logout": "Logout", "home": "Home"
    },
    "hi": {
        "login": "लॉगिन", "register": "रजिस्टर", "email": "ईमेल पता",
        "password": "पासवर्ड", "account_type": "खाता प्रकार",
        "public": "सार्वजनिक", "private": "निजी", "language": "भाषा",
        "tagline": "आपकी फ़ोटो। आपके नियम।", "link_accounts": "खाते जोड़ें",
        "trusted_friends": "विश्वसनीय मित्र", "ai_detection": "AI पहचान",
        "upload_photos": "फ़ोटो अपलोड करें", "logout": "लॉगआउट", "home": "होम"
    },
    "mr": {
        "login": "लॉगिन", "register": "नोंदणी", "email": "ईमेल पत्ता",
        "password": "पासवर्ड", "account_type": "खाते प्रकार",
        "public": "सार्वजनिक", "private": "खाजगी", "language": "भाषा",
        "tagline": "तुमचे फोटो. तुमचे नियम.", "link_accounts": "खाती जोडा",
        "trusted_friends": "विश्वासू मित्र", "ai_detection": "AI शोध",
        "upload_photos": "फोटो अपलोड करा", "logout": "लॉगआउट", "home": "मुख्यपृष्ठ"
    },
    "es": {
        "login": "Iniciar sesión", "register": "Registrarse", "email": "Correo electrónico",
        "password": "Contraseña", "account_type": "Tipo de cuenta",
        "public": "Público", "private": "Privado", "language": "Idioma",
        "tagline": "Tus fotos. Tus reglas.", "link_accounts": "Vincular cuentas",
        "trusted_friends": "Amigos de confianza", "ai_detection": "Detección IA",
        "upload_photos": "Subir fotos", "logout": "Cerrar sesión", "home": "Inicio"
    },
    "fr": {
        "login": "Connexion", "register": "S'inscrire", "email": "Adresse e-mail",
        "password": "Mot de passe", "account_type": "Type de compte",
        "public": "Public", "private": "Privé", "language": "Langue",
        "tagline": "Vos photos. Vos règles.", "link_accounts": "Lier les comptes",
        "trusted_friends": "Amis de confiance", "ai_detection": "Détection IA",
        "upload_photos": "Télécharger des photos", "logout": "Déconnexion", "home": "Accueil"
    }
}

def get_t():
    return TRANSLATIONS.get(session.get('lang', 'en'), TRANSLATIONS['en'])

# ── AI detection (pixel-level heuristic, no API) ──────────────────────────────
def analyze_images(img1_bytes, img2_bytes):
    try:
        img1 = Image.open(io.BytesIO(img1_bytes)).convert('RGB').resize((256, 256))
        img2 = Image.open(io.BytesIO(img2_bytes)).convert('RGB').resize((256, 256))
        a1, a2 = np.array(img1, dtype=float), np.array(img2, dtype=float)
        similarity = max(0, 100 - (np.abs(a1 - a2).mean() / 2.55))
        gray2 = np.array(Image.open(io.BytesIO(img2_bytes)).convert('L').resize((256, 256)), dtype=float)
        noise = np.std(np.diff(gray2, axis=0)) + np.std(np.diff(gray2, axis=1))
        ai_prob = min(100, max(0, (noise / 15) * 100))
        return {
            'similarity': round(similarity, 1),
            'ai_probability': round(ai_prob, 1),
            'verdict': 'Likely AI-Generated / Morphed' if ai_prob > 55 else 'Likely Authentic',
            'match': 'High Match' if similarity > 70 else ('Partial Match' if similarity > 40 else 'Low Match'),
            'is_ai': ai_prob > 55
        }
    except Exception as e:
        return {'error': str(e)}

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        email  = request.form.get('email', '').strip().lower()
        pw     = request.form.get('password', '')
        lang   = request.form.get('lang', 'en')
        session['lang'] = lang

        if action == 'register':
            if email in USERS:
                flash('Email already registered.', 'error')
            else:
                acct = request.form.get('account_type', 'private')
                USERS[email] = {'password': pw, 'account_type': acct, 'lang': lang}
                TRUSTED[email] = []
                UPLOADS[email] = []
                SOCIAL_LINKS[email] = {}
                session['user'] = email
                session['account_type'] = acct
                return redirect(url_for('home_private' if acct == 'private' else 'home_public'))

        elif action == 'login':
            u = USERS.get(email)
            if u and u['password'] == pw:
                session['user'] = email
                session['account_type'] = u['account_type']
                session['lang'] = u.get('lang', 'en')
                return redirect(url_for('home_private' if u['account_type'] == 'private' else 'home_public'))
            flash('Invalid email or password.', 'error')

    return render_template('login.html', t=get_t(),
                           current_lang=session.get('lang', 'en'))

@app.route('/home/private')
def home_private():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('home_private.html', t=get_t(), user=session['user'])

@app.route('/home/public')
def home_public():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('home_public.html', t=get_t(), user=session['user'])

@app.route('/link-accounts', methods=['GET', 'POST'])
def link_accounts():
    if 'user' not in session: return redirect(url_for('login'))
    email = session['user']
    if request.method == 'POST':
        SOCIAL_LINKS[email] = {p: request.form.get(p, '') for p in
                               ['instagram','snapchat','twitter','facebook','linkedin','tiktok']}
        flash('Accounts linked successfully!', 'success')
    return render_template('link_accounts.html', t=get_t(),
                           links=SOCIAL_LINKS.get(email, {}),
                           user=email, account_type=session.get('account_type'))

@app.route('/trusted-friends', methods=['GET', 'POST'])
def trusted_friends():
    if 'user' not in session: return redirect(url_for('login'))
    email = session['user']
    if request.method == 'POST':
        action    = request.form.get('action')
        friend_id = request.form.get('friend_id', '').strip()
        if action == 'add' and friend_id and friend_id not in TRUSTED.get(email, []):
            TRUSTED.setdefault(email, []).append(friend_id)
            flash(f'{friend_id} added to trusted friends.', 'success')
        elif action == 'remove' and friend_id in TRUSTED.get(email, []):
            TRUSTED[email].remove(friend_id)
            flash(f'{friend_id} removed.', 'info')
    return render_template('trusted_friends.html', t=get_t(),
                           friends=TRUSTED.get(email, []),
                           user=email, account_type=session.get('account_type'))

@app.route('/ai-detection', methods=['GET', 'POST'])
def ai_detection():
    if 'user' not in session: return redirect(url_for('login'))
    result = None
    if request.method == 'POST':
        orig    = request.files.get('original_photo')
        suspect = request.files.get('suspect_photo')
        if orig and suspect:
            result = analyze_images(orig.read(), suspect.read())
    return render_template('ai_detection.html', t=get_t(), result=result,
                           user=session['user'], account_type=session.get('account_type'))

@app.route('/upload-photos', methods=['GET', 'POST'])
def upload_photos():
    if 'user' not in session: return redirect(url_for('login'))
    email = session['user']
    if request.method == 'POST':
        files = request.files.getlist('photos')
        saved = 0
        for f in files:
            if f and f.filename:
                name = f"{email.split('@')[0]}_{f.filename}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
                UPLOADS.setdefault(email, []).append(name)
                saved += 1
        if saved:
            flash(f'{saved} photo(s) uploaded and protected.', 'success')
    return render_template('upload_photos.html', t=get_t(),
                           photos=UPLOADS.get(email, []), user=email)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)