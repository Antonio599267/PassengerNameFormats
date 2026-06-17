import streamlit as st
import re

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Air India – Flight Booking",
    page_icon="✈️",
    layout="wide",
)

# ─────────────────────────────────────────────
# Flight data – destination country drives all rules automatically
# ─────────────────────────────────────────────
FLIGHTS = {
    "AI 101  |  DEL → JFK  |  Tue 23 Jun 26  |  12:30 → 22:15": {
        "from": "DEL", "to": "JFK", "country": "US",
        "display_from": "DEL", "display_to": "JFK",
        "dep": "12:30", "arr": "22:15", "date": "TUE, 23 JUN 26", "price": "INR 45,200"
    },
    "AI 115  |  BOM → YYZ  |  Wed 24 Jun 26  |  08:00 → 16:30": {
        "from": "BOM", "to": "YYZ", "country": "CA",
        "display_from": "BOM", "display_to": "YYZ",
        "dep": "08:00", "arr": "16:30", "date": "WED, 24 JUN 26", "price": "INR 52,800"
    },
    "AI 302  |  DEL → SYD  |  Thu 25 Jun 26  |  09:15 → 06:45+1": {
        "from": "DEL", "to": "SYD", "country": "AU",
        "display_from": "DEL", "display_to": "SYD",
        "dep": "09:15", "arr": "06:45", "date": "THU, 25 JUN 26", "price": "INR 61,400"
    },
    "AI 314  |  DEL → AKL  |  Fri 26 Jun 26  |  11:00 → 09:30+1": {
        "from": "DEL", "to": "AKL", "country": "NZ",
        "display_from": "DEL", "display_to": "AKL",
        "dep": "11:00", "arr": "09:30", "date": "FRI, 26 JUN 26", "price": "INR 58,900"
    },
    "AI 202  |  DEL → HYD  |  Tue 23 Jun 26  |  12:30 → 14:45": {
        "from": "DEL", "to": "HYD", "country": "IN",
        "display_from": "DEL", "display_to": "HYD",
        "dep": "12:30", "arr": "14:45", "date": "TUE, 23 JUN 26", "price": "INR 7,543"
    },
    "AI 803  |  MUC → DEL  |  Mon 30 Jun 26  |  14:00 → 01:30+1": {
        "from": "MUC", "to": "DEL", "country": "IN",
        "display_from": "MUC", "display_to": "DEL",
        "dep": "14:00", "arr": "01:30", "date": "MON, 30 JUN 26", "price": "INR 38,750"
    },
}

# ─────────────────────────────────────────────
# CSS – close to real Air India UI
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* ── Top nav ── */
    .ai-nav {
        background: white;
        padding: 0 32px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 0;
    }
    .ai-logo { color: #C8102E; font-size: 1.5rem; font-weight: 900; letter-spacing: 1px; padding: 14px 0; }
    .ai-logo span { color: #F0A500; }

    /* ── Progress stepper ── */
    .stepper {
        background: white;
        border-bottom: 1px solid #ddd;
        display: flex;
        justify-content: center;
        gap: 0;
        margin-bottom: 0;
    }
    .step {
        padding: 14px 48px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #aaa;
        border-bottom: 3px solid transparent;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .step.active { color: #C8102E; border-bottom: 3px solid #C8102E; }
    .step.done   { color: #28a745; border-bottom: 3px solid #28a745; }
    .step-num {
        width: 22px; height: 22px; border-radius: 50%;
        background: #ddd; color: white;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 0.72rem; font-weight: 700;
    }
    .step.active .step-num { background: #C8102E; }
    .step.done   .step-num { background: #28a745; }

    /* ── Flight bar ── */
    .flight-bar {
        background: white;
        border-bottom: 1px solid #e0e0e0;
        padding: 12px 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.88rem;
    }
    .flight-bar .times { font-size: 1.5rem; font-weight: 700; color: #111; }
    .flight-bar .label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
    .flight-bar .iata  { font-size: 1rem; font-weight: 700; color: #333; }
    .flight-bar .price-label { font-size: 0.72rem; color: #888; }
    .flight-bar .price-val { font-size: 1.4rem; font-weight: 700; color: #111; }
    .flight-bar .price-link { color: #C8102E; font-size: 0.82rem; cursor: pointer; }
    .flight-arrow { color: #C8102E; font-size: 1.1rem; margin: 0 8px; }

    /* ── Main content ── */
    .main-wrap { max-width: 900px; margin: 32px auto; padding: 0 16px; }

    /* ── Section heading ── */
    .pax-heading {
        color: #C8102E;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 18px;
        margin-top: 8px;
    }

    /* ── Info card ── */
    .info-card {
        background: #EAF4FB;
        border: 1px solid #B8D9EE;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 20px;
        font-size: 0.88rem;
        color: #1a4a6b;
    }
    .info-card b { color: #1a4a6b; }
    .info-card ul { margin: 6px 0 0 18px; padding: 0; }
    .info-card li { margin-bottom: 2px; }

    /* ── Form card ── */
    .form-card {
        background: white;
        border-radius: 8px;
        padding: 28px 32px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        margin-bottom: 20px;
    }
    .form-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #111;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }

    /* ── Country badge ── */
    .country-badge {
        display: inline-block;
        background: #fff3cd;
        border: 1px solid #ffc107;
        color: #7a5200;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-left: 10px;
    }

    /* ── Validation boxes ── */
    .v-error {
        background: #fdf3f4; border-left: 4px solid #C8102E;
        padding: 14px 18px; border-radius: 6px;
        font-size: 0.9rem; color: #6b0a14; margin-top: 14px;
    }
    .v-warning {
        background: #fffbf0; border-left: 4px solid #F0A500;
        padding: 14px 18px; border-radius: 6px;
        font-size: 0.9rem; color: #5a3d00; margin-top: 14px;
    }
    .v-success {
        background: #f0faf3; border-left: 4px solid #28a745;
        padding: 14px 18px; border-radius: 6px;
        font-size: 0.9rem; color: #145227; margin-top: 14px;
    }

    /* ── Button override ── */
    .stButton > button {
        background-color: #C8102E !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        padding: 10px 32px !important;
    }
    .stButton > button:hover { background-color: #a00d24 !important; }

    /* ─────────────────────────────────────────
       DARK MODE – activates automatically when the
       user's OS / browser is set to dark
    ───────────────────────────────────────────── */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #0e1117; }

        .ai-nav {
            background: #181c24;
            border-bottom: 1px solid #2a2f3a;
        }

        .stepper {
            background: #181c24;
            border-bottom: 1px solid #2a2f3a;
        }
        .step { color: #7d8597; }
        .step.active { color: #ff5c72; border-bottom: 3px solid #ff5c72; }
        .step.done   { color: #3ddc84; border-bottom: 3px solid #3ddc84; }
        .step-num { background: #3a3f4b; color: #e6e6e6; }
        .step.active .step-num { background: #ff5c72; color: #181c24; }
        .step.done   .step-num { background: #3ddc84; color: #181c24; }

        .flight-bar {
            background: #181c24;
            border-bottom: 1px solid #2a2f3a;
        }
        .flight-bar .times { color: #f5f5f5; }
        .flight-bar .label { color: #9aa3b2; }
        .flight-bar .iata  { color: #d6d9e0; }
        .flight-bar .price-label { color: #9aa3b2; }
        .flight-bar .price-val { color: #f5f5f5; }
        .flight-bar .price-link { color: #ff5c72; }
        .flight-arrow { color: #ff5c72; }

        .pax-heading { color: #ff5c72; }

        .info-card {
            background: #14222e;
            border: 1px solid #2a4258;
            color: #b9d6ec;
        }
        .info-card b { color: #d6ecfb; }

        .form-card {
            background: #181c24;
            box-shadow: 0 1px 6px rgba(0,0,0,0.4);
        }
        .form-card-title {
            color: #f5f5f5;
            border-bottom: 1px solid #2a2f3a;
        }

        .country-badge {
            background: #3a2f10;
            border: 1px solid #b8860b;
            color: #ffd873;
        }

        .v-error {
            background: #2a1418; border-left: 4px solid #ff5c72;
            color: #ffb3bd;
        }
        .v-warning {
            background: #2b2410; border-left: 4px solid #F0A500;
            color: #ffe1a3;
        }
        .v-success {
            background: #11261a; border-left: 4px solid #3ddc84;
            color: #b8f0cd;
        }

        .stButton > button {
            background-color: #ff5c72 !important;
            color: #181c24 !important;
        }
        .stButton > button:hover { background-color: #ff8595 !important; }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Top nav
# ─────────────────────────────────────────────
st.markdown("""
<div class="ai-nav">
    <div class="ai-logo">AIR <span>INDIA</span> ✈</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Stepper
# ─────────────────────────────────────────────
st.markdown("""
<div class="stepper">
    <div class="step done">
        <span class="step-num">✓</span> Flights
    </div>
    <div class="step active">
        <span class="step-num">2</span> Journey Details
    </div>
    <div class="step">
        <span class="step-num">3</span> Review &amp; Payment
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Flight selector (drives all rules)
# ─────────────────────────────────────────────
st.markdown('<div style="max-width:900px; margin: 24px auto 0 auto; padding: 0 16px;">', unsafe_allow_html=True)

selected_flight_key = st.selectbox(
    "Select your flight",
    list(FLIGHTS.keys()),
    help="Choose your flight. Destination country determines which naming rules apply automatically."
)
flight = FLIGHTS[selected_flight_key]
dest_country = flight["country"]

# ─────────────────────────────────────────────
# Flight bar (matches Air India UI)
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="flight-bar" style="border-radius:8px; margin-bottom:20px; margin-top:8px;">
    <div>
        <div class="label">{flight['date']}</div>
        <div style="display:flex; align-items:center; gap:6px; margin-top:4px;">
            <div>
                <div class="times">{flight['dep']}</div>
                <div class="iata">{flight['display_from']}</div>
            </div>
            <div style="text-align:center; padding: 0 12px;">
                <div class="flight-arrow">✈ ············ ✈</div>
                <div class="label">Departure</div>
            </div>
            <div>
                <div class="times">{flight['arr']}</div>
                <div class="iata">{flight['display_to']}</div>
            </div>
        </div>
    </div>
    <div style="text-align:right;">
        <div class="price-label">Total Fare (1 Passenger)</div>
        <div class="price-val">{flight['price']}</div>
        <div class="price-link">Booking Summary ▼</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Auto-detect country flags
# ─────────────────────────────────────────────
is_us      = dest_country == "US"
is_canada  = dest_country == "CA"
is_us_ca   = dest_country in ("US", "CA")
is_aus     = dest_country == "AU"
is_nz      = dest_country == "NZ"
is_aus_nz  = dest_country in ("AU", "NZ")

COUNTRY_LABELS = {"US": "🇺🇸 USA", "CA": "🇨🇦 Canada", "AU": "🇦🇺 Australia",
                  "NZ": "🇳🇿 New Zealand", "IN": "🇮🇳 India", "OTHER": "Other"}
country_badge = COUNTRY_LABELS.get(dest_country, "Other")

# ─────────────────────────────────────────────
# Passenger details heading
# ─────────────────────────────────────────────
st.markdown(f'<div class="pax-heading">Passenger Details <span class="country-badge">Destination: {country_badge}</span></div>', unsafe_allow_html=True)

# Info box
st.markdown("""
<div class="info-card">
    <b>ℹ INFO</b>
    <ul>
        <li>Fields with an asterisk (*) are mandatory to fill in.</li>
        <li>Please provide your full name as given in your valid travel document.
            Names are automatically validated against Air India's naming conventions.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Form card
# ─────────────────────────────────────────────
st.markdown('<div class="form-card-title">Please Enter Passenger Details</div>', unsafe_allow_html=True)

col_title, col_fn, col_ln = st.columns([1, 2.5, 2.5])
with col_title:
    title = st.selectbox("Title *", ["MR", "MRS", "MS", "MISS", "DR", "PROF"])
with col_fn:
    first_name = st.text_input(
        "First Name (& Middle Name, if any) *",
        placeholder="e.g. JOHN FITZGERALD",
        help="Enter first name and middle name separated by a space. No hyphens or apostrophes."
    )
with col_ln:
    last_name = st.text_input(
        "Surname / Last Name *",
        placeholder="e.g. KENNEDY",
        help="Enter surname only. No hyphens or apostrophes."
    )

col_dob, col_mrz = st.columns([1, 2])
with col_dob:
    dob = st.text_input("Date of Birth *", placeholder="DD/MM/YYYY")
with col_mrz:
    passport_mrz = st.text_input(
        "Passport Name as in the MRZ *",
        placeholder="e.g. P<PHLDELA<CRUZ<<MARIA",
        help="Enter the full MRZ line exactly as printed (e.g. P<PHLDELA<CRUZ<<MARIA)."
    )

# Checkbox: no surname
no_surname = st.checkbox("I do not have a surname / family name on my travel document")

# ─────────────────────────────────────────────
# Validation logic
# ─────────────────────────────────────────────
def parse_mrz_name(mrz_raw):
    """
    Parse the 'Passport Name as in the MRZ Zone' field.

    Accepts either:
      - A full MRZ line, e.g.  "P<PHLDELA<CRUZ<<MARIA"
      - A name-only fragment,  e.g.  "DELA<CRUZ<<MARIA" or "CRUZ<<MARIA"

    Returns (surname, given_name) as uppercase strings with '<' converted
    to spaces and collapsed. Either part may be empty if not present.
    """
    if not mrz_raw:
        return "", ""

    s = mrz_raw.strip().upper()

    # Strip a leading document-code + issuing-country prefix, e.g. "P<PHL" or "P<USA".
    # Real MRZ lines start with a document type letter, '<' filler, then the
    # 3-letter issuing country code. Only strip if this exact pattern is found.
    m = re.match(r"^[A-Z]<[A-Z]{3}", s)
    if m:
        s = s[m.end():]

    s = s.strip("<")  # remove any leading/trailing filler

    if "<<" in s:
        surname_part, given_part = s.split("<<", 1)
    else:
        # No surname/given separator found — treat whole thing as given name
        surname_part, given_part = "", s

    surname = re.sub(r"<+", " ", surname_part).strip()
    given = re.sub(r"<+", " ", given_part).strip()

    return surname, given


def validate_air_india(title, first_name, last_name, no_surname,
                       is_us_ca, is_canada, is_aus_nz, is_aus, is_nz,
                       passport_mrz=""):
    issues = []
    ln = last_name.strip().upper()
    fn = first_name.strip().upper()

    mrz_surname, mrz_given = parse_mrz_name(passport_mrz)
    # Full given name from MRZ (may be multi-word, e.g. "PRAMOD KUMAR")
    mrz_name = mrz_given.strip()

    # ── No surname rules ──────────────────────────────────────────────────────
    if no_surname:
        # Determine the given name: whatever is in fn, falling back to ln
        given = fn if fn else ln

        if is_canada:
            # Correct format: ln == "LNU" and fn is a real name (not empty, not LNU)
            format_ok = ln == "LNU" and fn and fn != "LNU"
            # Extra check: fn must match MRZ given name (if MRZ was provided)
            mrz_mismatch = bool(mrz_name) and fn != mrz_name
            if format_ok and mrz_mismatch:
                issues.append(("error",
                    f"⚠️ **Name mismatch with MRZ Zone (Canada – No Surname)**\n\n"
                    f"The First Name **`{fn}`** does not match the given name in the MRZ Zone "
                    f"(**`{mrz_name}`**).\n\n"
                    f"The booking should be processed as: **{title} {mrz_name} LNU**\n\n"
                    "📌 Correct entry:\n"
                    f"> **Title** → `{title}` | **First Name** → `{mrz_name}` | **Last Name** → `LNU`"
                ))
            elif format_ok:
                issues.append(("success",
                    f"✅ Booking will be processed as: **{title} {fn} LNU**"
                ))
            else:
                issues.append(("error",
                    "⚠️ **No Surname / Family Name – Canada Exception**\n\n"
                    "For flights to/from **Canada**, enter **LNU** in the Last Name field "
                    "and your given name(s) in the First Name field, followed by the title.\n\n"
                    "📌 **Example:**\n"
                    f"> Enter as: **Title** → `{title}` | **First Name** → `{given or 'JEREMY'}` | **Last Name** → `LNU`"
                ))

        elif is_aus or is_nz:
            country_label = "Australia" if is_aus else "New Zealand"
            format_ok = fn and ln and fn == ln
            mrz_mismatch = bool(mrz_name) and fn != mrz_name
            if format_ok and mrz_mismatch:
                issues.append(("error",
                    f"⚠️ **Name mismatch with MRZ Zone ({country_label} – No Surname)**\n\n"
                    f"The name **`{fn}`** does not match the given name in the MRZ Zone "
                    f"(**`{mrz_name}`**).\n\n"
                    f"The booking should be processed as: **{title} {mrz_name} {mrz_name}**\n\n"
                    "📌 Correct entry:\n"
                    f"> **Title** → `{title}` | **First Name** → `{mrz_name}` | **Last Name** → `{mrz_name}`"
                ))
            elif format_ok:
                issues.append(("success",
                    f"✅ Booking will be processed as: **{title} {fn} {ln}**"
                ))
            else:
                issues.append(("error",
                    f"⚠️ **No Surname / Family Name – {country_label} Exception**\n\n"
                    f"For flights to/from **{country_label}**, repeat the given name in **both** "
                    "the First Name and Last Name fields.\n\n"
                    "📌 **Example:**\n"
                    f"> Enter as: **Title** → `{title}` | **First Name** → `{given or 'JEREMY'}` | **Last Name** → `{given or 'JEREMY'}`"
                ))

        else:
            # General case: correct if fn is FNU or fn == title, and ln contains the given name
            option_a_ok = fn == "FNU" and ln and ln not in ("FNU",)
            option_b_ok = fn == title.upper() and ln and ln != title.upper()
            format_ok = option_a_ok or option_b_ok

            # MRZ mismatch check: the Last Name should equal the MRZ given name
            mrz_mismatch = bool(mrz_name) and ln != mrz_name

            if format_ok and mrz_mismatch:
                # The format itself is right but the Last Name doesn't match the MRZ
                correct_fn = title.upper() if option_b_ok else "FNU"
                issues.append(("error",
                    f"⚠️ **Name mismatch with MRZ Zone (No Surname)**\n\n"
                    f"The Last Name **`{ln}`** does not match the given name in the MRZ Zone "
                    f"(**`{mrz_name}`**).\n\n"
                    f"The booking should be processed as: **{title} {correct_fn} {mrz_name}**\n\n"
                    "📌 Correct entry:\n"
                    f"> **Title** → `{title}` | **First Name** → `{correct_fn}` | **Last Name** → `{mrz_name}`"
                ))
            elif format_ok:
                issues.append(("success",
                    f"✅ Booking will be processed as: **{title} {fn} {ln}**"
                ))
            else:
                issues.append(("error",
                    "⚠️ **No Surname / Family Name Detected**\n\n"
                    "When no surname is available and all names appear under the Given Name header "
                    "of the travel document, use one of these formats:\n\n"
                    "**Option A:** Enter given name(s) in the Last Name field and add **FNU** "
                    "(First Name Unknown) in the First Name field.\n"
                    f"> **Title** → `{title}` | **First Name** → `FNU` | **Last Name** → `{given or 'JEREMY'}`\n\n"
                    "**Option B:** Enter given name(s) in the Last Name field and repeat the title "
                    "in the First Name field.\n"
                    f"> **Title** → `{title}` | **First Name** → `{title}` | **Last Name** → `{given or 'JEREMY'}`"
                ))
        return issues

    # ── Rule 1a: Hyphen or apostrophe in surname ─────────────────────────────
    # Only flag if there's still a hyphen/apostrophe — if user already fixed it (space instead), pass
    if re.search(r"[-']", ln):
        issues.append(("error",
            "⚠️ **Hyphen or apostrophe detected in the Last Name field.**\n\n"
            "Air India does not allow hyphens or apostrophes in the surname field. "
            "Delete the hyphen or apostrophe and replace with a **space**.\n\n"
            "📌 **Example:**\n"
            "> Passport: `JAMES ROBERT BRYCE-BUCHANAN`\n"
            "> Enter as: **Title** → `MR` | **First Name** → `JAMES ROBERT` | **Last Name** → `BRYCE BUCHANAN`"
        ))

    # ── Rule 1b: Hyphen or apostrophe in first/middle name ───────────────────
    if re.search(r"[-']", fn):
        issues.append(("error",
            "⚠️ **Hyphen or apostrophe detected in the First Name field.**\n\n"
            "Air India does not allow hyphens or apostrophes in the first/middle name field. "
            "Delete the hyphen or apostrophe and replace with a **space**.\n\n"
            "📌 **Example:**\n"
            "> Passport: `MARY-JANE`\n"
            "> Enter as: **First Name** → `MARY JANE`"
        ))

    # ── Rule 2: Single letter in surname ────────────────────────────────────
    # Flag only if single letter; if user doubled it (e.g. YY) it passes through
    if re.fullmatch(r"[A-Z]", ln):
        issues.append(("error",
            "⚠️ **Single letter detected in the Last Name field.**\n\n"
            "Repeat the single letter as the Last Name, and enter your given names "
            "in the First Name field.\n\n"
            "📌 **Example:**\n"
            "> Passport: `MISS SMITH Y`\n"
            "> Enter as: **Title** → `MISS` | **First Name** → `SMITH` | **Last Name** → `YY`"
        ))

    # ── Rule 3: Middle name required for US / Canada ─────────────────────────
    # Only relevant if the passenger actually has a surname per the MRZ Zone.
    # If the MRZ Zone shows no surname, the "no surname" workflow / checkbox applies instead.
    if is_us_ca and fn and mrz_surname:
        name_parts = fn.split()
        if len(name_parts) < 2:
            dest_label = "United States" if not is_canada else "Canada"
            issues.append(("warning",
                f"⚠️ **Middle name missing for a {dest_label} flight.**\n\n"
                "For flights to or from the **United States or Canada**, the middle name is "
                "**mandatory** and must be included in the First Name field.\n\n"
                "📌 **Example:**\n"
                "> Passport: `JOHN FITZGERALD KENNEDY`\n"
                "> Enter as: **Title** → `MR` | **First Name** → `JOHN FITZGERALD` | **Last Name** → `KENNEDY`"
            ))

    # ── Rule 4: Name must match the MRZ Zone ─────────────────────────────────
    if passport_mrz.strip():
        mrz_full_name = f"{mrz_given} {mrz_surname}".strip() if mrz_surname else mrz_given
        entered_full_name = f"{fn} {ln}".strip()

        # Compare token sets so word order differences don't cause false negatives,
        # while still catching genuinely different / missing names.
        mrz_tokens = set(mrz_full_name.split())
        entered_tokens = set(entered_full_name.split())

        if mrz_tokens and mrz_tokens != entered_tokens:
            issues.append(("error",
                "⚠️ **Name does not match the Passport MRZ Zone.**\n\n"
                f"You entered: **{title} {entered_full_name}**\n\n"
                f"The MRZ Zone shows: **{mrz_given}{' ' + mrz_surname if mrz_surname else ''}**\n\n"
                "Please make sure the First Name and Last Name fields exactly match the name "
                "in your passport's MRZ Zone (the '<' characters are ignored)."
            ))

    # ── All good ─────────────────────────────────────────────────────────────
    if ln and fn and not issues:
        issues.append(("success",
            f"✅ Booking will be processed as: **{title} {fn} {ln}**"
        ))

    if not ln and not fn:
        issues = []

    return issues


# ─────────────────────────────────────────────
# Validate button
# ─────────────────────────────────────────────
validate_btn = st.button("Validate Name & Continue →", use_container_width=False)

if validate_btn:
    # Always recompute from the CURRENT field values — never reuse cached results,
    # so every click re-validates against whatever is in the fields right now.
    st.session_state["last_validation_inputs"] = {
        "title": title, "first_name": first_name, "last_name": last_name,
        "no_surname": no_surname, "passport_mrz": passport_mrz,
    }

    if not no_surname and (not first_name.strip() or not last_name.strip()):
        st.session_state["last_validation_results"] = None
        st.markdown("""
        <div class="v-error">❌ Please fill in both <b>First Name</b> and <b>Surname/Last Name</b> before continuing.</div>
        """, unsafe_allow_html=True)
    else:
        results = validate_air_india(
            title, first_name, last_name, no_surname,
            is_us_ca, is_canada, is_aus_nz, is_aus, is_nz,
            passport_mrz=passport_mrz
        )
        st.session_state["last_validation_results"] = results

        for severity, msg in results:
            css_class = {"error": "v-error", "warning": "v-warning", "success": "v-success"}.get(severity, "v-error")
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            st.markdown(msg)
            st.markdown('</div>', unsafe_allow_html=True)

        errors = [r for r in results if r[0] == "error"]
        if not errors and results:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Confirm Booking"):
                st.balloons()
                st.success(f"🎉 Booking confirmed for **{title} {first_name.strip().upper()} {last_name.strip().upper()}**!")

st.markdown('</div>', unsafe_allow_html=True)  # close main-wrap

# ── Footer ───────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#bbb; font-size:0.78rem;'>"
    "Prototype – Air India naming convention validation demo. Not an official Air India product."
    "</center>",
    unsafe_allow_html=True
)
