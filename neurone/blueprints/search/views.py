from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
import pytz
from datetime import datetime
import math
import pandas as pd
from keras.models import load_model
import uuid
import babel.numbers
import math
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
from lib.util_json import render_json
from neurone.blueprints.search.decorators import credits_required
import os
import openai
import markdown
from neurone.extensions import db
from neurone.blueprints.user.models import User
from neurone.blueprints.search.forms import NeuroneForm
from neurone.blueprints.search.models.search import Neurone_entries as Ne
from neurone.blueprints.search.models.search import (
    Countries,
    Industries,
    NeuroneDB as Ndb)

search = Blueprint(
    "search", __name__, template_folder="templates", url_prefix="/search"
)


@search.before_request
@login_required
def before_request():
    """Protect all of the search endpoints."""
    pass


@search.route('/results/<key>', methods=['GET', 'POST'])
@login_required
def results(key):
    info = ['Last year revenue', 'Last year EBITDA', 'Last year FCFF',
            'Previous year revenue', '3-5 years historical revenue CAGR',
            '3-5 years forecasted CAGR', 'Percentage of recurring revenue',
            'Country', 'Industry', 'Listed company?', 'Search Name',
            'Search ID']
    entr = Ne.query.filter_by(key=key).first()
    brev0 = babel.numbers.format_decimal(entr.rev0, None, 'en_GB', False)
    bebitda = babel.numbers.format_decimal(entr.ebitda, None, 'en_GB', False)
    brev1 = babel.numbers.format_decimal(entr.rev1, None, 'en_GB', False)
    bfcff = babel.numbers.format_decimal(entr.fcff, None, 'en_GB', False)
    info1 = [brev0, bebitda, bfcff, brev1, entr.hcagr, entr.fcagr, entr.arr,
             entr.country, entr.industry, entr.listed, entr.pj_name, entr.key]

    res = Ndb.query.filter_by(key=key).first()
    info2 = [babel.numbers.format_decimal(res.low,
                                          '#,##0.##;-#',
                                          'en_GB'),
             babel.numbers.format_decimal(res.high,
                                          '#,##0.##;-#',
                                          'en_GB'),
             babel.numbers.format_decimal(res.EV_EBITDA,
                                          '#,##0.##;-#',
                                          'en_GB'),
             babel.numbers.format_decimal(res.low*entr.ebitda,
                                          '#,##0;-#',
                                          'en_GB'),
             babel.numbers.format_decimal(res.high*entr.ebitda,
                                          '#,##0;-#',
                                          'en_GB'),
             babel.numbers.format_decimal(res.EV_EBITDA*entr.ebitda,
                                          '#,##0;-#',
                                          'en_GB')]
    html = res.report1
    html2 = res.report2
    indu = Industries.query.filter_by(industry=entr.industry).first()
    mmul = indu.multiple

    lg = res.low
    rg = res.EV_EBITDA - res.low - 0.1
    mg = res.high - res.EV_EBITDA + 0.1
    minimo = math.floor(min(lg, mmul) - 1)
    massimo = math.ceil(max(res.high, mmul) + 1)

    info3 = [lg, rg, mg, minimo, massimo]

    return render_template('search/results.html',
                           info=info, info1=info1, info2=info2,
                           info3=info3, mmul=mmul, industry=entr.industry,
                           html=html, html2=html2)



@search.route('/neurone', methods=['GET', 'POST'])
#@credits_required
@login_required
def neurone():
    form = NeuroneForm()
    user = current_user
    cred = current_user.credits

    if form.validate_on_submit():
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rev0 = float(form.Rev0.data)
        ebitda = float(form.Ebitda.data)
        fcff = float(form.Fcff.data)
        rev1 = float(form.Rev1.data)
        hcagr = float(form.Hcagr.data)
        fcagr = float(form.Fcagr.data)
        ann = float(form.Arr.data)
        country = form.Country.data.country
        industry = form.Industry.data.industry
        listed = int(form.Listed.data)
        pj_name = form.pjn.data
        email = current_user.email
        ebitdaperc = ebitda/rev0
        growth = ((hcagr+fcagr)/200)+1
        if rev0 < 30000:
            small = 0
            medium = 0
            big = 0.95
        elif rev0 >= 50000:
            small = 0
            medium = 0
            big = 1
        else:
            small = 0
            medium = 0
            big = 0.98
        arr = ann/100
        market = 16.04
        sandp = -0.1944
        cashebitda = fcff/ebitda
        rule40 = ebitdaperc + ((rev0/rev1)-1)
        if rule40 >= 0.5:
            itssw = 1
        else:
            itssw = 0
        itslisted = listed
        countryrank = Countries.query.filter_by(country=country).first().rank
        ind = Industries.query.filter_by(industry=industry).first().multiple
        uid = str(uuid.uuid1())
        adj1 = math.log10(math.exp(arr))
        adj2 = math.log10(ind)

        data = Ne(rev0=rev0, ebitda=ebitda, fcff=fcff, rev1=rev1,
                  hcagr=hcagr, fcagr=fcagr, arr=ann, country=country,
                  industry=industry, listed=listed, entry_date=now,
                  pj_name=pj_name, email=email, key=uid, user_id=user.id,
                  created_on=now)

        data2 = [ebitdaperc, growth, small, medium, big, market, sandp,
                 cashebitda, rule40, itssw, int(itslisted), countryrank]
        dvi = pd.DataFrame(columns=['ebitdaperc', 'growth', 'small',
                                    'medium', 'big', 'market_EV',
                                    'SP_yield', 'cash_ebitda', 'rule40',
                                    'itsSW', 'itsListed', 'country_rank'])
        dvi.loc[0] = data2

        model_path = 'assets/app/Neurone_v1.0.0.h5'
        model = load_model(model_path)
        result = model.predict(dvi)

        if ind >= result[0, 2]:
            result = result+adj1+adj2
        else:
            result = result+adj1-adj2

        lm = float(result[0, 0])
        mm = float(result[0, 1])
        rm = float(result[0, 2])
        lp = lm*ebitda
        mp = mm*ebitda
        rp = rm*ebitda

        # OpenAI reports
        openai.api_key = os.environ["OPENAI_KEY"]
        q = ('can you explain why the value of the company below is ' + str(rm) + 'x EBITDA while the industry average is '
             + str(ind) + 'x EBITDA: Revenue is ' + str(rev0) + 'K, EBITDA ' + str(ebitda) + 'K, FCFF '
             + str(fcff) + 'K, Last year revenue ' + str(rev1) + 'K, ' + str(hcagr) + '% historical revenue CAGR, and '
             + str(fcagr) + '% future revenue CAGR, ' + str(ann) + '% recurring revenue, headquartered in '
             + str(country) + ', and active in ' + str(industry) + '. Last year growth was ' + str((rev0 / rev1) - 1)
             + ', the rule of forty is ' + str(rule40) + ' and its Ebitda Margin is ' + str(ebitdaperc))

        q2 = (
            'prepare a short report of the {} industry in {}. including average profitability, key players, etc.').format(
            str(industry), str(country))

        chat_completion = openai.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": q
                }
            ],
            model="gpt-4o-mini",
            max_tokens = 1000,  # number of words
            temperature = 0)  # 0 very predictable; 2 very deterministic
        output = chat_completion.choices[0].message.content
        html = markdown.markdown(output)
        chat_completion2 = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": q2
                }
            ],
            model="gpt-4o-mini",
            max_tokens=1000,  # number of words
            temperature=0)  # 0 very predictable; 2 very deterministic
        output2 = chat_completion2.choices[0].message.content
        html2 = markdown.markdown(output2)

        data3 = Ndb(low=lm, high=mm, EV_EBITDA=rm, ebitda_perc=ebitdaperc,
                    growth=growth, small=small, medium=medium, big=big,
                    market_EV=market, SP_yield=sandp, cash_ebitda=cashebitda,
                    rule40=rule40, itsSW=itssw, itsListed=int(itslisted),
                    country_rank=countryrank, submit_date=now, pj_name=pj_name,
                    key=uid, email=email, user_id=user.id, report1=html, report2=html2)
        db.session.add(data)
        db.session.add(data3)
        user = User.query.filter_by(email=email).first()
        user.credits = cred-1
        user.last_search_on = datetime.now(pytz.utc)
        db.session.commit()
        info = ['Last year revenue', 'Last year EBITDA', 'Last year FCFF',
                'Previous year revenue', '3-5 years historical revenue CAGR',
                '3-5 years forecasted CAGR', 'Percentage of recurring revenue',
                'Country', 'Industry', 'Listed company?',
                'Search Name', 'Search ID']
        brev0 = babel.numbers.format_decimal(rev0, None, 'en_GB', False)
        bebitda = babel.numbers.format_decimal(ebitda, None, 'en_GB', False)
        brev1 = babel.numbers.format_decimal(rev1, None, 'en_GB', False)
        bfcff = babel.numbers.format_decimal(fcff, None, 'en_GB', False)
        info1 = [brev0, bebitda, bfcff, brev1, hcagr, fcagr,
                 ann, country, industry, listed, pj_name, uid]
        info2 = [babel.numbers.format_decimal(lm, '#,##0.##;-#', 'en_GB'),
                 babel.numbers.format_decimal(mm, '#,##0.##;-#', 'en_GB'),
                 babel.numbers.format_decimal(rm, '#,##0.##;-#', 'en_GB'),
                 babel.numbers.format_decimal(lp, '#,##0;-#', 'en_GB'),
                 babel.numbers.format_decimal(mp, '#,##0;-#', 'en_GB'),
                 babel.numbers.format_decimal(rp, '#,##0;-#', 'en_GB')]

        indu = Industries.query.filter_by(industry=industry).first()
        mmul = indu.multiple

        lg = lm
        rg = rm - lm - 0.1
        mg = mm - rm + 0.1
        minimo = math.floor(min(lm, mmul) - 1)
        massimo = math.ceil(max(mm, mmul) + 1)

        info3 = [lg, rg, mg, minimo, massimo]


        return render_template('search/results.html',
                               key=uid, info=info, info1=info1,
                               info2=info2, info3=info3, mmul=mmul, industry=industry,
                               html=html, html2=html2)

    return render_template('search/neurone.html',
                           form=form, user=user, cred=cred)
