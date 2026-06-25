import os
from functools import wraps
from flask import Flask, request, redirect, url_for, flash, session, render_template_string
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "agrilink-dev-secret")

def db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST","localhost"),
        user=os.getenv("MYSQL_USER","root"),
        password=os.getenv("MYSQL_PASSWORD",""),
        database=os.getenv("MYSQL_DATABASE","agrilink_sl"),
        port=int(os.getenv("MYSQL_PORT","3306"))
    )

def rows(sql,p=()):
    c=db(); cur=c.cursor(dictionary=True); cur.execute(sql,p); r=cur.fetchall(); cur.close(); c.close(); return r
def row(sql,p=()):
    c=db(); cur=c.cursor(dictionary=True); cur.execute(sql,p); r=cur.fetchone(); cur.close(); c.close(); return r
def execsql(sql,p=()):
    c=db(); cur=c.cursor(); cur.execute(sql,p); c.commit(); cur.close(); c.close()

def verify(stored, pw):
    if stored == pw:
        return True

    try:
        return check_password_hash(stored, pw)
    except Exception:
        return False

def must_login(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get("uid"):
            flash("Please login first.","warning"); return redirect("/login")
        return f(*a,**k)
    return w

def must_admin(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get("uid"):
            flash("Please login first.","warning"); return redirect("/login")
        if session.get("role")!="admin":
            flash("Admin access only.","danger"); return redirect("/farmer")
        return f(*a,**k)
    return w

STYLE = """
<style>
:root{
    --g:#116b3a;
    --d:#082719;
    --m:#6d7d73;
    --bg:#f3fbf4;
    --r:24px;
    --sh:0 20px 60px rgba(8,39,25,.12)
}

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Inter,Arial,sans-serif;
    background:linear-gradient(#fbfff9,#edf8ef);
    color:var(--d);
    overflow-x:hidden;
}

a{
    text-decoration:none;
    color:inherit;
}

.nav{
    position:sticky;
    top:0;
    z-index:5;
    padding:18px 6%;
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:rgba(255,255,255,.88);
    backdrop-filter:blur(14px);
    border-bottom:1px solid #d8edde;
}

.brand{
    font-size:22px;
    font-weight:900;
    color:var(--g);
}

.links{
    display:flex;
    gap:20px;
    align-items:center;
    font-weight:800;
}

.btn{
    display:inline-block;
    border:0;
    border-radius:999px;
    background:var(--g);
    color:#fff;
    padding:12px 18px;
    font-weight:900;
    cursor:pointer;
}

.ghost{
    background:#fff;
    color:var(--g);
    border:1px solid #cfe7d5;
}

.badge{
    display:inline-block;
    background:#e5f7e9;
    color:var(--g);
    padding:8px 14px;
    border-radius:999px;
    font-size:12px;
    font-weight:900;
    text-transform:uppercase;
}

.hero{
    min-height:78vh;
    padding:70px 6%;
    display:grid;
    grid-template-columns:1.05fr .95fr;
    gap:42px;
    align-items:center;
}

.hero h1,
.head h1,
.auth h1{
    font-size:clamp(38px,6vw,72px);
    line-height:.98;
    letter-spacing:-.05em;
    margin:18px 0;
}

.hero p,
.head p,
.auth p{
    font-size:18px;
    line-height:1.7;
    color:var(--m);
}

.hero-card{
    min-height:420px;
    border-radius:40px;
    background:radial-gradient(circle at top,#dfffba,transparent 38%),linear-gradient(135deg,var(--g),#072817);
    display:grid;
    place-items:center;
    box-shadow:var(--sh);
}

.phone{
    background:#fff;
    border:8px solid #10291d;
    border-radius:32px;
    padding:30px;
    width:min(360px,90%);
    box-shadow:0 30px 80px rgba(0,0,0,.25);
}

.code{
    background:#eef8f0;
    border-radius:18px;
    padding:14px;
    font-weight:900;
    color:var(--g);
}

.section{
    padding:60px 6%;
}

.grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:20px;
}

.card,
.auth,
.table,
.filter,
.stat{
    background:rgba(255,255,255,.92);
    border:1px solid #d9eddf;
    border-radius:var(--r);
    padding:24px;
    box-shadow:var(--sh);
}

.card p{
    color:var(--m);
    line-height:1.6;
}

.price strong,
.stat strong{
    font-size:30px;
    color:var(--g);
}

.auth{
    max-width:760px;
    margin:55px auto;
}

.narrow{
    max-width:520px;
}

form{
    display:grid;
    gap:14px;
}

label{
    font-weight:900;
}

input,
select,
textarea{
    width:100%;
    padding:15px;
    border:1px solid #cfe7d5;
    border-radius:16px;
    background:#fbfffb;
    font:inherit;
}

.two{
    grid-template-columns:1fr 1fr;
}

.span{
    grid-column:span 2;
}

.flash{
    max-width:950px;
    margin:14px auto;
    padding:14px 18px;
    background:white;
    border-radius:16px;
    box-shadow:var(--sh);
    font-weight:900;
}

.success{border-left:6px solid var(--g);}
.danger{border-left:6px solid #b42318;}
.warning{border-left:6px solid #f79009;}
.info{border-left:6px solid #1570ef;}

.dash{
    display:grid;
    grid-template-columns:270px 1fr;
    min-height:82vh;
}

.side{
    background:white;
    border-right:1px solid #d9eddf;
    padding:28px 18px;
    position:sticky;
    top:73px;
    height:calc(100vh - 73px);
}

.side h2{
    color:var(--g);
    margin-top:0;
}

.side a{
    display:block;
    padding:13px 14px;
    border-radius:16px;
    margin:6px 0;
    font-weight:900;
    color:#3d594b;
}

.side .on,
.side a:hover{
    background:#e5f7e9;
    color:var(--g);
}

.main{
    padding:34px 4%;
    overflow-x:auto;
}

.head{
    display:flex;
    justify-content:space-between;
    gap:20px;
    align-items:center;
    margin-bottom:24px;
}

.head h1{
    font-size:44px;
}

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    margin-bottom:24px;
}

.stat span{
    display:block;
    color:var(--m);
    font-weight:900;
}

.filter{
    display:grid;
    grid-template-columns:2fr 1fr 1fr auto;
    gap:12px;
    margin-bottom:24px;
}

.split{
    display:grid;
    grid-template-columns:.85fr 1.15fr;
    gap:24px;
    align-items:start;
}

table{
    width:100%;
    border-collapse:collapse;
}

.table{
    overflow-x:auto;
}

th,
td{
    text-align:left;
    padding:14px;
    border-bottom:1px solid #e0eee4;
}

th{
    font-size:12px;
    text-transform:uppercase;
    color:var(--m);
}

td strong{
    color:var(--g);
}

.small{
    border:0;
    border-radius:12px;
    padding:8px 12px;
    font-weight:900;
    cursor:pointer;
}

.del{
    background:#fee4e2;
    color:#b42318;
}

.ok{
    background:#dcfae6;
    color:#067647;
    border-radius:99px;
    padding:6px 10px;
    font-weight:900;
}

.bad{
    background:#fee4e2;
    color:#b42318;
    border-radius:99px;
    padding:6px 10px;
    font-weight:900;
}

.sms{
    background:#10291d;
    color:#fff;
    border-radius:22px;
    padding:22px;
    margin-top:20px;
}

.footer{
    display:flex;
    justify-content:space-between;
    padding:35px 6%;
    background:#092217;
    color:white;
}

.footer p{
    color:#b8cec2;
}

@media(max-width:950px){

    .hero,
    .split{
        grid-template-columns:1fr;
    }

    .dash{
        display:block;
    }

    .side{
        position:relative;
        top:0;
        height:auto;
        width:100%;
        border-right:none;
        border-bottom:1px solid #d9eddf;
    }

    .main{
        width:100%;
        padding:20px;
    }

    .grid,
    .stats{
        grid-template-columns:repeat(2,1fr);
    }

    .filter{
        grid-template-columns:1fr;
    }
}

@media(max-width:650px){

    .links{
        display:none;
    }

    .grid,
    .stats,
    .two{
        grid-template-columns:1fr;
    }

    .span{
        grid-column:span 1;
    }

    .footer{
        display:block;
    }
}
</style>
"""

BASE = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{{title}}</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap' rel='stylesheet'>"""+STYLE+"""</head><body><nav class='nav'><a class='brand' href='/'>🌱 AgriLink SL</a><div class='links'><a href='/'>Home</a><a href='/about'>About</a>{% if session.get('uid') %}{% if session.get('role')=='admin' %}<a href='/admin'>Admin</a>{% else %}<a href='/farmer'>Dashboard</a><a href='/prices'>Prices</a>{% endif %}<a class='btn' href='/logout'>Logout</a>{% else %}<a href='/login'>Login</a><a class='btn' href='/register'>Register</a>{% endif %}</div></nav>{% with msgs=get_flashed_messages(with_categories=true) %}{% for c,m in msgs %}<div class='flash {{c}}'>{{m}}</div>{% endfor %}{% endwith %}{{body|safe}}<footer class='footer'><div><b>AgriLink SL</b><p>Fair crop market information for small-scale farmers.</p></div><div>COMP 318 IT Project Management</div></footer></body></html>"""
def render(body,title="AgriLink SL",**ctx): return render_template_string(BASE, body=render_template_string(body,**ctx), title=title)

def side(role,active):
    if role=="admin": items=[("Dashboard","/admin"),("Crops","/admin/crops"),("Markets","/admin/markets"),("Prices","/admin/prices"),("Users","/admin/users"),("Reports","/admin/reports")]
    else: items=[("Dashboard","/farmer"),("Market Prices","/prices"),("SMS Simulator","/sms"),("USSD Simulator","/ussd"),("Price Alerts","/alerts"),("Notifications","/notifications"),("Profile","/profile")]
    return "<aside class='side'><h2>"+role.title()+"</h2>"+"".join(f"<a class='{'on' if active==n else ''}' href='{u}'>{n}</a>" for n,u in items)+"</aside>"

@app.route("/")
def home():
    latest=rows("SELECT p.*,c.name crop,m.name market,m.district FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id ORDER BY p.updated_at DESC LIMIT 6")
    b="""<section class='hero'><div><span class='badge'>Offline-first market information</span><h1>Connecting farmers to fair market prices.</h1><p>AgriLink SL helps farmers check crop prices, compare markets, and reduce exploitation caused by poor access to market information.</p><p><a class='btn' href='/login'>Check Prices</a> <a class='btn ghost' href='/register'>Create Farmer Account</a></p></div><div class='hero-card'><div class='phone'><h2>USSD / SMS Demo</h2><p class='code'>Dial *555#</p><p>Rice price in Bo Market: <b>NLe 620 / bag</b></p></div></div></section><section class='section'><center><span class='badge'>Why AgriLink?</span><h1>Built for Sierra Leonean farmers</h1></center><div class='grid'><div class='card'><h3>Transparent Prices</h3><p>Farmers can see current market prices before negotiating.</p></div><div class='card'><h3>SMS Ready</h3><p>Demonstrates basic phone price access.</p></div><div class='card'><h3>Market Coverage</h3><p>Prices are organised by crop, market, and district.</p></div><div class='card'><h3>Admin Verification</h3><p>Admins manage crops, markets, users, and prices.</p></div></div></section><section class='section'><center><span class='badge'>Latest Updates</span><h1>Recent Prices</h1></center><div class='grid'>{% for p in latest %}<div class='card price'><h3>{{p.crop}}</h3><p>{{p.market}}, {{p.district}}</p><strong>NLe {{p.price}} / {{p.unit}}</strong><p>{{p.updated_at}}</p></div>{% endfor %}</div></section>"""
    return render(b, latest=latest)

@app.route("/about")
def about():
    b="<section class='section'><div class='auth'><span class='badge'>Project Overview</span><h1>About AgriLink SL</h1><p>AgriLink SL solves weak access to crop market information among small-scale farmers. It provides farmer accounts, crop price lookup, admin-controlled data, reports, and an SMS/USSD simulation for low-connectivity environments.</p><h2>Users</h2><p><b>Farmer:</b> registers, logs in, searches prices, views crop details, and updates profile.</p><p><b>Admin:</b> manages crops, markets, prices, users, and reports.</p></div></section>"
    return render(b,"About")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        if request.form["password"]!=request.form["confirm_password"]: flash("Passwords do not match.","danger"); return redirect("/register")
        if row("SELECT id FROM users WHERE email=%s OR phone=%s",(request.form["email"],request.form["phone"])): flash("Email or phone already exists.","danger"); return redirect("/register")
        execsql("INSERT INTO users(full_name,email,phone,district,password_hash,role,is_active) VALUES(%s,%s,%s,%s,%s,'farmer',1)",(request.form["full_name"],request.form["email"].lower(),request.form["phone"],request.form["district"],generate_password_hash(request.form["password"])))
        flash("Registration successful. Login now.","success"); return redirect("/login")
    b="<section class='auth'><span class='badge'>Farmer Account</span><h1>Create Account</h1><form method='post' class='two'><div><label>Full Name</label><input name='full_name' required></div><div><label>Email</label><input type='email' name='email' required></div><div><label>Phone</label><input name='phone' required></div><div><label>District</label><input name='district' required></div><div><label>Password</label><input type='password' name='password' required></div><div><label>Confirm Password</label><input type='password' name='confirm_password' required></div><button class='btn span'>Register</button></form></section>"
    return render(b,"Register")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=row("SELECT * FROM users WHERE email=%s",(request.form["email"].lower(),))
        if not u or not verify(u["password_hash"],request.form["password"]): flash("Invalid email or password.","danger"); return redirect("/login")
        if not u["is_active"]: flash("Account disabled.","danger"); return redirect("/login")
        session.update(uid=u["id"],name=u["full_name"],role=u["role"])
        return redirect("/admin" if u["role"]=="admin" else "/farmer")
    b="<section class='auth narrow'><span class='badge'>Welcome Back</span><h1>Login</h1><form method='post'><label>Email</label><input type='email' name='email' required><label>Password</label><input type='password' name='password' required><button class='btn'>Login</button></form><div class='card' style='margin-top:18px'><b>Demo accounts</b><p>Admin: admin@agrilink.sl / admin123</p><p>Farmer: farmer@agrilink.sl / farmer123</p></div></section>"
    return render(b,"Login")

@app.route("/logout")
def logout(): session.clear(); flash("Logged out.","info"); return redirect("/")

@app.route("/farmer")
@must_login
def farmer():
    stats={"crops":row("SELECT COUNT(*) total FROM crops")["total"],"markets":row("SELECT COUNT(*) total FROM markets")["total"],"prices":row("SELECT COUNT(*) total FROM prices")["total"]}
    latest=rows("SELECT p.*,c.name crop,m.name market,m.district FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id ORDER BY p.updated_at DESC LIMIT 10")
    b=side("farmer","Dashboard")+"""<main class='main'><div class='head'><div><span class='badge'>Farmer Dashboard</span><h1>Welcome, {{session.name}}</h1><p>Check prices and make better selling decisions.</p></div><a class='btn' href='/prices'>View Prices</a></div><div class='stats'><div class='stat'><strong>{{stats.crops}}</strong><span>Crops</span></div><div class='stat'><strong>{{stats.markets}}</strong><span>Markets</span></div><div class='stat'><strong>{{stats.prices}}</strong><span>Price Records</span></div></div><div class='table'><h2>Latest Price Updates</h2><table><tr><th>Crop</th><th>Market</th><th>District</th><th>Price</th><th>Updated</th></tr>{% for p in latest %}<tr><td>{{p.crop}}</td><td>{{p.market}}</td><td>{{p.district}}</td><td><strong>NLe {{p.price}} / {{p.unit}}</strong></td><td>{{p.updated_at}}</td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", stats=stats, latest=latest)

@app.route("/prices")
@must_login
def prices():
    search=request.args.get("search",""); district=request.args.get("district",""); ctype=request.args.get("crop_type","")
    sql="SELECT p.*,c.id crop_id,c.name crop,c.crop_type,m.name market,m.district FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id WHERE 1=1"; p=[]
    if search: sql+=" AND c.name LIKE %s"; p.append("%"+search+"%")
    if district: sql+=" AND m.district=%s"; p.append(district)
    if ctype: sql+=" AND c.crop_type=%s"; p.append(ctype)
    data=rows(sql+" ORDER BY c.name,m.district",tuple(p)); districts=rows("SELECT DISTINCT district FROM markets ORDER BY district"); types=rows("SELECT DISTINCT crop_type FROM crops ORDER BY crop_type")
    b=side("farmer","Market Prices")+"""<main class='main'><div class='head'><div><span class='badge'>Market Prices</span><h1>Search and compare crop prices</h1></div></div><form class='filter'><input name='search' placeholder='Search crop...' value='{{search}}'><select name='district'><option value=''>All Districts</option>{% for d in districts %}<option {% if district==d.district %}selected{% endif %}>{{d.district}}</option>{% endfor %}</select><select name='crop_type'><option value=''>All Types</option>{% for t in types %}<option {% if ctype==t.crop_type %}selected{% endif %}>{{t.crop_type}}</option>{% endfor %}</select><button class='btn'>Filter</button></form><div class='table'><table><tr><th>Crop</th><th>Type</th><th>Market</th><th>District</th><th>Price</th><th>Action</th></tr>{% for x in data %}<tr><td>{{x.crop}}</td><td>{{x.crop_type}}</td><td>{{x.market}}</td><td>{{x.district}}</td><td><strong>NLe {{x.price}} / {{x.unit}}</strong></td><td><a class='btn ghost' href='/crop/{{x.crop_id}}'>Details</a></td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", data=data, districts=districts, types=types, search=search, district=district, ctype=ctype)

@app.route("/crop/<int:id>")
@must_login
def crop(id):
    c=row("SELECT * FROM crops WHERE id=%s",(id,)); data=rows("SELECT p.*,m.name market,m.district FROM prices p JOIN markets m ON p.market_id=m.id WHERE p.crop_id=%s ORDER BY p.updated_at DESC",(id,))
    b=side("farmer","Market Prices")+"""<main class='main'><div class='card'><span class='badge'>{{c.crop_type}}</span><h1>{{c.name}}</h1><p>{{c.description}}</p></div><div class='table'><h2>Market Records</h2><table><tr><th>Market</th><th>District</th><th>Price</th><th>Note</th><th>Updated</th></tr>{% for x in data %}<tr><td>{{x.market}}</td><td>{{x.district}}</td><td><strong>NLe {{x.price}} / {{x.unit}}</strong></td><td>{{x.note or '-'}}</td><td>{{x.updated_at}}</td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", c=c, data=data)

@app.route("/sms",methods=["GET","POST"])
@must_login
def sms():
    result=None
    if request.method=="POST":
        x=row("SELECT c.name crop,m.name market,m.district,p.price,p.unit,p.updated_at FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id WHERE c.name LIKE %s ORDER BY p.updated_at DESC LIMIT 1",("%"+request.form["crop"]+"%",))
        result=f"AGRILINK SL: {x['crop']} is NLe {x['price']} per {x['unit']} at {x['market']}, {x['district']}. Updated: {x['updated_at']}." if x else "AGRILINK SL: No price found for that crop."
    b=side("farmer","SMS Simulator")+"""<main class='main'><div class='card'><span class='badge'>Demo Feature</span><h1>SMS / USSD Price Simulation</h1><p>Shows how a basic phone farmer could request crop prices without internet.</p><form method='post'><label>Crop Name</label><input name='crop' placeholder='Rice, Cassava...' required><button class='btn'>Simulate SMS Reply</button></form>{% if result %}<div class='sms'>{{result}}</div>{% endif %}</div></main>"""
    return render("<section class='dash'>"+b+"</section>", result=result)

@app.route("/ussd", methods=["GET","POST"])
@must_login
def ussd():

    step = request.form.get("step","1")
    crop_id = request.form.get("crop_id")

    crops = rows(
        "SELECT id,name FROM crops ORDER BY name"
    )

    result = None

    if crop_id:

        result = rows("""
            SELECT
                c.name crop,
                m.name market,
                m.district,
                p.price,
                p.unit
            FROM prices p
            JOIN crops c ON p.crop_id=c.id
            JOIN markets m ON p.market_id=m.id
            WHERE c.id=%s
            ORDER BY m.district
        """,(crop_id,))

    b = side("farmer","USSD Simulator") + """
    <main class='main'>

        <div class='card'>

            <span class='badge'>USSD DEMO</span>

            <h1>*555# Simulator</h1>

            <p>
            Demonstrates how a farmer using a basic phone
            can access market prices without using a smartphone.
            </p>

            <form method='post'>

                <label>Select Crop</label>

                <select name='crop_id' required>

                    <option value=''>
                    1. Select Crop
                    </option>

                    {% for c in crops %}
                    <option value='{{c.id}}'>
                    {{c.name}}
                    </option>
                    {% endfor %}

                </select>

                <br><br>

                <button class='btn'>
                Continue
                </button>

            </form>

        </div>

        {% if result %}

        <div class='sms'>

            <h2>
            USSD RESPONSE
            </h2>

            {% for r in result %}

            <p>

            <b>{{r.crop}}</b><br>

            {{r.market}} ({{r.district}})<br>

            NLe {{r.price}} / {{r.unit}}

            </p>

            {% endfor %}

        </div>

        {% endif %}

    </main>
    """

    return render(
        "<section class='dash'>"+b+"</section>",
        crops=crops,
        result=result
    )

@app.route("/alerts", methods=["GET","POST"])
@must_login
def alerts():

    if request.method=="POST":

        execsql("""
            INSERT INTO price_alerts
            (user_id,crop_id,market_id,target_price)
            VALUES(%s,%s,%s,%s)
        """,(
            session["uid"],
            request.form["crop_id"],
            request.form["market_id"],
            request.form["target_price"]
        ))

        flash("Price alert created.","success")
        return redirect("/alerts")

    crops = rows(
        "SELECT * FROM crops ORDER BY name"
    )

    markets = rows(
        "SELECT * FROM markets ORDER BY name"
    )

    alerts = rows("""
        SELECT
            a.*,
            c.name crop,
            m.name market
        FROM price_alerts a
        JOIN crops c ON a.crop_id=c.id
        JOIN markets m ON a.market_id=m.id
        WHERE a.user_id=%s
        ORDER BY a.id DESC
    """,(session["uid"],))

    b = side("farmer","Price Alerts") + """
    <main class='main'>

        <div class='card'>

            <span class='badge'>
            PRICE ALERTS
            </span>

            <h1>Create Alert</h1>

            <form method='post'>

                <label>Crop</label>
                <select name='crop_id' required>

                    {% for c in crops %}
                    <option value='{{c.id}}'>
                    {{c.name}}
                    </option>
                    {% endfor %}

                </select>

                <label>Market</label>
                <select name='market_id' required>

                    {% for m in markets %}
                    <option value='{{m.id}}'>
                    {{m.name}}
                    </option>
                    {% endfor %}

                </select>

                <label>Target Price</label>
                <input
                    type='number'
                    step='0.01'
                    name='target_price'
                    required
                >

                <button class='btn'>
                Save Alert
                </button>

            </form>

        </div>

        <div class='table' style='margin-top:20px'>

            <h2>Your Alerts</h2>

            <table>

                <tr>
                    <th>Crop</th>
                    <th>Market</th>
                    <th>Target Price</th>
                </tr>

                {% for a in alerts %}
                <tr>

                    <td>{{a.crop}}</td>

                    <td>{{a.market}}</td>

                    <td>
                    NLe {{a.target_price}}
                    </td>

                </tr>
                {% endfor %}

            </table>

        </div>

    </main>
    """

    return render(
        "<section class='dash'>"+b+"</section>",
        crops=crops,
        markets=markets,
        alerts=alerts
    )

@app.route("/notifications")
@must_login
def notifications():

    data = rows("""
        SELECT *
        FROM notifications
        WHERE user_id=%s
        ORDER BY created_at DESC
    """,(session["uid"],))

    b = side("farmer","Notifications")+"""
    <main class='main'>

        <div class='card'>

            <span class='badge'>
            Notifications
            </span>

            <h1>Your Alerts</h1>

        </div>

        {% for n in data %}

        <div class='sms'>

            <p>
            {{n.message}}
            </p>

            <small>
            {{n.created_at}}
            </small>

        </div>

        <br>

        {% endfor %}

    </main>
    """

    return render(
        "<section class='dash'>"+b+"</section>",
        data=data
    )       

@app.route("/profile",methods=["GET","POST"])
@must_login
def profile():
    u=row("SELECT * FROM users WHERE id=%s",(session["uid"],))
    if request.method=="POST":
        execsql("UPDATE users SET full_name=%s,phone=%s,district=%s WHERE id=%s",(request.form["full_name"],request.form["phone"],request.form["district"],session["uid"]))
        session["name"]=request.form["full_name"]; flash("Profile updated.","success"); return redirect("/profile")
    b=side("farmer","Profile")+"""<main class='main'><div class='card'><span class='badge'>Account</span><h1>Your Profile</h1><form method='post' class='two'><div><label>Name</label><input name='full_name' value='{{u.full_name}}'></div><div><label>Email</label><input value='{{u.email}}' disabled></div><div><label>Phone</label><input name='phone' value='{{u.phone}}'></div><div><label>District</label><input name='district' value='{{u.district}}'></div><button class='btn span'>Update Profile</button></form></div></main>"""
    return render("<section class='dash'>"+b+"</section>", u=u)


@app.route("/admin")
@must_admin
def admin():
    stats={"farmers":row("SELECT COUNT(*) total FROM users WHERE role='farmer'")["total"],"crops":row("SELECT COUNT(*) total FROM crops")["total"],"markets":row("SELECT COUNT(*) total FROM markets")["total"],"prices":row("SELECT COUNT(*) total FROM prices")["total"]}
    latest=rows("SELECT p.*,c.name crop,m.name market,m.district FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id ORDER BY p.updated_at DESC LIMIT 10")
    b=side("admin","Dashboard")+"""<main class='main'><div class='head'><div><span class='badge'>Admin Control Panel</span><h1>System Overview</h1></div></div><div class='stats'><div class='stat'><strong>{{stats.farmers}}</strong><span>Farmers</span></div><div class='stat'><strong>{{stats.crops}}</strong><span>Crops</span></div><div class='stat'><strong>{{stats.markets}}</strong><span>Markets</span></div><div class='stat'><strong>{{stats.prices}}</strong><span>Prices</span></div></div><div class='table'><h2>Recent Price Updates</h2><table><tr><th>Crop</th><th>Market</th><th>District</th><th>Price</th><th>Updated</th></tr>{% for p in latest %}<tr><td>{{p.crop}}</td><td>{{p.market}}</td><td>{{p.district}}</td><td><strong>NLe {{p.price}} / {{p.unit}}</strong></td><td>{{p.updated_at}}</td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", stats=stats, latest=latest)

@app.route("/admin/crops",methods=["GET","POST"])
@must_admin
def acrops():
    if request.method=="POST": execsql("INSERT INTO crops(name,crop_type,description) VALUES(%s,%s,%s)",(request.form["name"],request.form["crop_type"],request.form["description"])); flash("Crop added.","success"); return redirect("/admin/crops")
    data=rows("SELECT * FROM crops ORDER BY name")
    b=side("admin","Crops")+"""<main class='main'><div class='split'><div class='card'><span class='badge'>Add Crop</span><h1>New Crop</h1><form method='post'><label>Name</label><input name='name' required><label>Type</label><input name='crop_type' required><label>Description</label><textarea name='description'></textarea><button class='btn'>Save</button></form></div><div class='table'><h2>Crop List</h2><table><tr><th>Name</th><th>Type</th><th>Action</th></tr>{% for x in data %}<tr><td>{{x.name}}</td><td>{{x.crop_type}}</td><td><form method='post' action='/admin/crops/{{x.id}}/delete'><button class='small del'>Delete</button></form></td></tr>{% endfor %}</table></div></div></main>"""
    return render("<section class='dash'>"+b+"</section>", data=data)

@app.route("/admin/crops/<int:id>/delete",methods=["POST"])
@must_admin
def dcrop(id): execsql("DELETE FROM crops WHERE id=%s",(id,)); flash("Crop deleted.","info"); return redirect("/admin/crops")

@app.route("/admin/markets",methods=["GET","POST"])
@must_admin
def amarkets():
    if request.method=="POST": execsql("INSERT INTO markets(name,district) VALUES(%s,%s)",(request.form["name"],request.form["district"])); flash("Market added.","success"); return redirect("/admin/markets")
    data=rows("SELECT * FROM markets ORDER BY district,name")
    b=side("admin","Markets")+"""<main class='main'><div class='split'><div class='card'><span class='badge'>Add Market</span><h1>New Market</h1><form method='post'><label>Market Name</label><input name='name' required><label>District</label><input name='district' required><button class='btn'>Save</button></form></div><div class='table'><h2>Market List</h2><table><tr><th>Name</th><th>District</th><th>Action</th></tr>{% for x in data %}<tr><td>{{x.name}}</td><td>{{x.district}}</td><td><form method='post' action='/admin/markets/{{x.id}}/delete'><button class='small del'>Delete</button></form></td></tr>{% endfor %}</table></div></div></main>"""
    return render("<section class='dash'>"+b+"</section>", data=data)

@app.route("/admin/markets/<int:id>/delete",methods=["POST"])
@must_admin
def dmarket(id): execsql("DELETE FROM markets WHERE id=%s",(id,)); flash("Market deleted.","info"); return redirect("/admin/markets")

@app.route("/admin/prices",methods=["GET","POST"])
@must_admin
def aprices():
    if request.method=="POST":

        execsql(
            "INSERT INTO prices(crop_id,market_id,price,unit,note,updated_by) VALUES(%s,%s,%s,%s,%s,%s)",
            (
                request.form["crop_id"],
                request.form["market_id"],
                request.form["price"],
                request.form["unit"],
                request.form["note"],
                session["uid"]
            )
        )

        matches = rows("""
            SELECT *
            FROM price_alerts
            WHERE crop_id=%s
            AND market_id=%s
            AND target_price<=%s
        """,(
            request.form["crop_id"],
            request.form["market_id"],
            request.form["price"]
        ))

        crop = row(
            "SELECT name FROM crops WHERE id=%s",
            (request.form["crop_id"],)
        )

        market = row(
            "SELECT name FROM markets WHERE id=%s",
            (request.form["market_id"],)
        )

        for a in matches:

            msg = f"""
        AGRILINK ALERT

        {crop['name']} in {market['name']}
        has reached NLe {request.form['price']} per {request.form['unit']}.

        Your target was NLe {a['target_price']}.
        """

            execsql(
                """
                INSERT INTO notifications(user_id,message)
                VALUES(%s,%s)
                """,
                (
                    a["user_id"],
                    msg
                )
            )

        flash("Price saved.","success")
        return redirect("/admin/prices")
    crops=rows("SELECT * FROM crops ORDER BY name"); markets=rows("SELECT * FROM markets ORDER BY district,name"); data=rows("SELECT p.*,c.name crop,m.name market,m.district FROM prices p JOIN crops c ON p.crop_id=c.id JOIN markets m ON p.market_id=m.id ORDER BY p.updated_at DESC")
    b=side("admin","Prices")+"""<main class='main'><div class='card'><span class='badge'>Price Management</span><h1>Add Price Update</h1><form method='post' class='two'><div><label>Crop</label><select name='crop_id'>{% for c in crops %}<option value='{{c.id}}'>{{c.name}}</option>{% endfor %}</select></div><div><label>Market</label><select name='market_id'>{% for m in markets %}<option value='{{m.id}}'>{{m.name}} - {{m.district}}</option>{% endfor %}</select></div><div><label>Price</label><input type='number' step='0.01' name='price' required></div><div><label>Unit</label><input name='unit' value='kg' required></div><div class='span'><label>Note</label><input name='note'></div><button class='btn span'>Save Price</button></form></div><div class='table'><h2>All Prices</h2><table><tr><th>Crop</th><th>Market</th><th>District</th><th>Price</th><th>Action</th></tr>{% for x in data %}<tr><td>{{x.crop}}</td><td>{{x.market}}</td><td>{{x.district}}</td><td><strong>NLe {{x.price}} / {{x.unit}}</strong></td><td><form method='post' action='/admin/prices/{{x.id}}/delete'><button class='small del'>Delete</button></form></td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", crops=crops, markets=markets, data=data)

@app.route("/admin/prices/<int:id>/delete",methods=["POST"])
@must_admin
def dprice(id): execsql("DELETE FROM prices WHERE id=%s",(id,)); flash("Price deleted.","info"); return redirect("/admin/prices")

@app.route("/admin/users")
@must_admin
def users():
    data=rows("SELECT * FROM users ORDER BY created_at DESC")
    b=side("admin","Users")+"""<main class='main'><div class='table'><h1>System Users</h1><table><tr><th>Name</th><th>Email</th><th>Phone</th><th>District</th><th>Role</th><th>Status</th><th>Action</th></tr>{% for u in data %}<tr><td>{{u.full_name}}</td><td>{{u.email}}</td><td>{{u.phone}}</td><td>{{u.district}}</td><td>{{u.role}}</td><td>{% if u.is_active %}<span class='ok'>Active</span>{% else %}<span class='bad'>Disabled</span>{% endif %}</td><td>{% if u.role!='admin' %}<form method='post' action='/admin/users/{{u.id}}/toggle'><button class='small'>Toggle</button></form>{% else %}-{% endif %}</td></tr>{% endfor %}</table></div></main>"""
    return render("<section class='dash'>"+b+"</section>", data=data)

@app.route("/admin/users/<int:id>/toggle",methods=["POST"])
@must_admin
def toggle(id):
    u=row("SELECT is_active FROM users WHERE id=%s",(id,)); execsql("UPDATE users SET is_active=%s WHERE id=%s",(0 if u["is_active"] else 1,id)); flash("User status updated.","success"); return redirect("/admin/users")

@app.route("/admin/reports")
@must_admin
def reports():
    crop=rows("SELECT c.name crop,COUNT(p.id) total FROM crops c LEFT JOIN prices p ON c.id=p.crop_id GROUP BY c.id ORDER BY total DESC")
    farmer=rows("SELECT district,COUNT(*) total FROM users WHERE role='farmer' GROUP BY district ORDER BY total DESC")
    b=side("admin","Reports")+"""<main class='main'><div class='head'><div><span class='badge'>Reports</span><h1>System Analytics</h1></div></div><div class='split'><div class='table'><h2>Price Updates by Crop</h2><table><tr><th>Crop</th><th>Total Updates</th></tr>{% for x in crop %}<tr><td>{{x.crop}}</td><td>{{x.total}}</td></tr>{% endfor %}</table></div><div class='table'><h2>Farmers by District</h2><table><tr><th>District</th><th>Farmers</th></tr>{% for x in farmer %}<tr><td>{{x.district}}</td><td>{{x.total}}</td></tr>{% endfor %}</table></div></div></main>"""
    return render("<section class='dash'>"+b+"</section>", crop=crop, farmer=farmer)

if __name__=="__main__":
    app.run(debug=True)
