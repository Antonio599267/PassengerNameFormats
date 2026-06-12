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
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-card-title">Please Enter Passenger Details</div>', unsafe_allow_html=True)

col_title, col_fn, col_ln = st.columns([1, 2.5, 2.5])
with col_title:
    title = st.selectbox("Title *", ["MR", "MRS", "MS", "MISS", "DR", "PROF"])
with col_fn:
    first_name = st.text_input(
        "First Name (& Middle Name, if any) *",
        placeholder="e.g. JOHN FITZGERALD",
        help="Enter first name and middle name separated by a space."
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
        "Passport Name as in the MRZ Zone *",
        placeholder="e.g. KENNEDY<<JOHN<FITZGERALD<<<<<<",
        help="Machine-readable zone at the bottom of your passport photo page."
    )

# Checkbox: no surname
no_surname = st.checkbox("I do not have a surname / family name on my travel document")

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Validation logic
# ─────────────────────────────────────────────
def validate_air_india(title, first_name, last_name, no_surname,
                       is_us_ca, is_canada, is_aus_nz, is_aus, is_nz,
                       passport_mrz=""):
    issues = []
    ln = last_name.strip().upper()
    fn = first_name.strip().upper()

    # ── Helper: extract given name(s) from MRZ field ─────────────────────────
    # MRZ field may contain "<<" separators (e.g. "KENNEDY<<JOHN") or be plain text
    def mrz_given_name(mrz_raw):
        """Return the given-name portion from the MRZ Name field, uppercased."""
        if not mrz_raw:
            return ""
        s = mrz_raw.strip().upper()
        # If user typed the full MRZ line (SURNAME<<GIVEN<MIDDLE<<<) take given part
        if "<<" in s:
            parts = s.split("<<", 1)
            given_part = parts[1].replace("<", " ").strip() if len(parts) > 1 else ""
            return given_part.split()[0] if given_part else ""
        # Otherwise treat the whole field as the given name (single word expected)
        return s.split()[0] if s else ""

    mrz_name = mrz_given_name(passport_mrz)   # normalised first given name from MRZ

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
                    f"✅ **No Surname – Canada format correctly applied.**\n\n"
                    f"Booking will be processed as: **{title} {fn} LNU**\n\n"
                    "This matches Air India's convention for passengers without a surname on Canada flights."
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
                    f"✅ **No Surname – {country_label} format correctly applied.**\n\n"
                    f"Booking will be processed as: **{title} {fn} {ln}**\n\n"
                    f"This matches Air India's convention for passengers without a surname on {country_label} flights."
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

            # ── NEW: MRZ mismatch check ──────────────────────────────────────
            # For Option B (fn == title), the Last Name should equal the MRZ given name
            # For Option A (fn == FNU),   the Last Name should equal the MRZ given name
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
                    f"✅ **No Surname – format correctly applied.**\n\n"
                    f"Booking will be processed as: **{title} {fn} {ln}**\n\n"
                    "This matches Air India's convention for passengers without a surname."
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

    # ── Rule 1: Hyphen or apostrophe in surname ──────────────────────────────
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
    if is_us_ca and fn:
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

    # ── All good ─────────────────────────────────────────────────────────────
    if ln and fn and not issues:
        issues.append(("success",
            f"✅ **Name format looks correct for Air India.**\n\n"
            f"Booking will be processed as: **{title} {fn} {ln}**\n\n"
            "Please verify this matches your passport MRZ zone exactly before confirming."
        ))

    if not ln and not fn:
        issues = []

    return issues


# ─────────────────────────────────────────────
# Validate button
# ─────────────────────────────────────────────
validate_btn = st.button("Validate Name & Continue →", use_container_width=False)

if validate_btn:
    if not no_surname and (not first_name.strip() or not last_name.strip()):
        st.markdown("""
        <div class="v-error">❌ Please fill in both <b>First Name</b> and <b>Surname/Last Name</b> before continuing.</div>
        """, unsafe_allow_html=True)
    else:
        results = validate_air_india(
            title, first_name, last_name, no_surname,
            is_us_ca, is_canada, is_aus_nz, is_aus, is_nz,
            passport_mrz=passport_mrz
        )
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
