from flask import Flask, flash, request, redirect, render_template, url_for, make_response, Response, send_file, jsonify
from flask_navigation import Navigation
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError
import pdfkit, uuid, datetime, os, html #removed bleach as it is deprecated)
import pandas as pd
from boltons.iterutils import remap #to include in report
import itertools, operator #to include in report
from pdf2docx import parse #to include in report
from collections import Counter # to include in report
import json, plotly #to include in report (might remove, since using chart.js)
import plotly.express as px #to include in report (might remove, since using chart.js)
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import logging

# Define path to wkhtmltopdf.exe
path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Point pdfkit configuration to wkhtmltopdf.exe
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

app = Flask(__name__)
SITE_NAME = "https://localhostL5000"
nav = Navigation(app)
csrf = CSRFProtect(app)

foo = uuid.uuid4().hex
app.secret_key = foo

nav.Bar('top', [
    nav.Item('Main', 'index'),
    nav.Item('Revalidate', 'revalidate'),
    nav.Item('Guides', 'guides'),
    nav.Item('Scripts', 'scripts'),
])

ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_PATH'] = 'uploads'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clear_dir():
    folder_path = r"uploads"
    for fname in os.listdir(folder_path):
        file_path = os.path.join(folder_path, fname)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


class ReportForm(FlaskForm):
    dateformat = '%Y-%m-%d'
    companyname = StringField('Company Name:', validators=[InputRequired(), Length(min=2, max=200)], render_kw={"placeholder": "Enter the company's name here", "style": "width: 250px;"})
    companyabbv = StringField('Abbreviated Name:', validators=[InputRequired(), Length(min=2, max=30)], render_kw={"placeholder": "Enter the abbreviated name here", "style": "width: 250px;"})
    startdate = DateField('Start Date:', format=dateformat, validators=[InputRequired()])
    enddate = DateField('End Date:', format=dateformat, validators=[InputRequired()])
    generate = SubmitField('Download')

    def validate_on_submit(self, form):
        if form.enddate.data < form.startdate.data:
            flash(u"Please take note that the end date should not be earlier than the start date.", 'error')
        else:
            return True


@app.route('/', methods=['POST', 'GET'])
def index():
    clear_dir()
    if request.method == 'POST':
        f = request.files['fileUpload']
        if f.filename == '':
            return redirect(request.url)
        elif f and not allowed_file(f.filename):
            return redirect(request.url)
        elif f and allowed_file(f.filename):
            index.filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], index.filename))
            index.form = ReportForm()
            return redirect(url_for('analysis'))
    else:
        return render_template('index.html')


def replace(file):
    if 'Risk' not in file.columns:
        newheader = {'Severity':'Risk', 'Summary':'Description', 'NVT Name':'Name', 'IP':'Host'}
        file.rename(columns=newheader, inplace=True)
    return file


@app.route('/analysis')
def analysis():
    inputcsv = pd.read_csv(f"uploads/{index.filename}", keep_default_na=False)
    replace(inputcsv)

    inputcsv = inputcsv.drop(inputcsv[inputcsv['Risk'] == 'None'].index)
    inputcsv = inputcsv.drop(inputcsv[inputcsv['Risk'] == 'Low'].index)
    inputcsv = inputcsv.drop(inputcsv[inputcsv['Risk'] == 'Log'].index)

    result = inputcsv.to_dict('records')

    name_database = pd.read_csv("static/name_database.csv", keep_default_na=False)
    namedb = name_database.to_dict()
    # Cleaning empty values in the nested namedb dictionary
    drop_keys = lambda path, key, value: len(value) != 0
    cleandb = remap(namedb, visit=drop_keys)
    conversion_database = pd.read_csv("static/conversion.csv", keep_default_na=False)
    conversiondb = conversion_database.to_dict('records')

    analysis.filtered = []
    for i in result:
        analysis.filtered.append(i)

    for i in analysis.filtered:
        for keys, values in cleandb.items():
            for k, v in values.items():
                if i['Name'] == v:
                    i['Name'] = keys

    getvals = operator.itemgetter('Host', 'Name')
    analysis.filtered.sort(key=getvals)
    res = []
    for k, g in itertools.groupby(analysis.filtered, getvals):
        res.append(next(g))
    analysis.filtered[:] = res

    for i in analysis.filtered:
        for j in conversiondb:
            if i['Name'] == j['Name']:
                i['Description'] = j['Description']
                i['Solution'] = j['Solution']

    # Retrieving the list of hosts in the CSV file
    analysis.hosts = []
    for i in analysis.filtered:
        if i['Host'] not in analysis.hosts:
            analysis.hosts.append(i['Host'])
    analysis.hosts.sort()

    analysis.solutions = []
    for i in analysis.filtered:
        if i['Solution'] not in analysis.solutions:
            analysis.solutions.append(i['Solution'])

    analysis.names = []
    for i in analysis.filtered:
        if i['Name'] not in analysis.names:
            analysis.names.append(i['Name'])

    analysis.host_solutions = {}
    for i in analysis.filtered:
        if i['Host'] not in analysis.host_solutions:
            analysis.host_solutions[i['Host']] = [i['Solution']]
        if i['Solution'] not in analysis.host_solutions[i['Host']]:
            analysis.host_solutions[i['Host']].append(i['Solution'])

    for keys, values in analysis.host_solutions.items():
        values = list(set(values))
        analysis.host_solutions.update({keys:values})

    analysis.solutions_hosts = {}
    for i in analysis.filtered:
        if i['Solution'] not in analysis.solutions_hosts:
            analysis.solutions_hosts[i['Solution']] = [i['Host']]
        if i['Host'] not in analysis.solutions_hosts[i['Solution']]:
            analysis.solutions_hosts[i['Solution']].append(i['Host'])

    for keys, values in analysis.solutions_hosts.items():
        values = list(set(values))
        analysis.solutions_hosts.update({keys:values})

    analysis.solutions_risk = {}
    for i in analysis.filtered:
        if i['Solution'] not in analysis.solutions_risk:
            analysis.solutions_risk[i['Solution']] = [i['Risk']]
        if i['Risk'] not in analysis.solutions_risk[i['Solution']]:
            analysis.solutions_risk[i['Solution']].append(i['Risk'])

    for keys, values in analysis.solutions_risk.items():
        if 'Critical' in values:
            values = ['Critical']
        if 'High' in values:
            values = ['High']
        analysis.solutions_risk.update({keys:values})

    filtered_df = pd.DataFrame(analysis.filtered)

    analysis.nested_solutions = {k: f.groupby('Risk')['Description'].apply(list).to_dict() for k, f in filtered_df.groupby('Solution')}

    for main_keys, main_values in analysis.nested_solutions.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    analysis.nested_risks = {k: f.groupby('Solution')['Description'].apply(list).to_dict() for k, f in filtered_df.groupby('Risk')}

    for main_keys, main_values in analysis.nested_risks.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    analysis.nested_name = {k: f.groupby('Solution')['Host'].apply(list).to_dict() for k, f in filtered_df.groupby('Name')}

    for main_keys, main_values in analysis.nested_risks.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    # Graphs

    analysis.num_critical = 0
    analysis.num_high = 0
    num_medium = 0

    if 'Critical' in inputcsv['Risk'].values:
        analysis.num_critical = inputcsv['Risk'].value_counts()['Critical']
    if 'High' in inputcsv['Risk'].values:
        analysis.num_high = inputcsv['Risk'].value_counts()['High']
    if 'Medium' in inputcsv['Risk'].values:
        num_medium = inputcsv['Risk'].value_counts()['Medium']

    count_data = {"Legends":{"Severity":"Count"}, "#F44336":{"Critical":analysis.num_critical}, "#FF9F40":{"High":analysis.num_high}, "#FFCD56":{"Medium":num_medium}}

    count_hosts_data = inputcsv['Host'].value_counts().to_dict()
    count_hosts_data = dict(Counter(count_hosts_data).most_common(5))
    count_hosts = {"Host":"Count"}
    count_hosts.update(count_hosts_data)

    count_vulns_data = filtered_df['Name'].value_counts().to_dict()
    count_vulns_data = dict(Counter(count_vulns_data).most_common(5))
    count_vulns = {"Vulnerabilities":"Count"}
    count_vulns.update(count_vulns_data)

    # Total number of vulns for each host (for Report)
    analysis.hosts_vuln_count = {}
    for i in analysis.hosts:
        critical_dataframe = inputcsv.loc[(inputcsv['Host'] == i) & (inputcsv['Risk'] == 'Critical')]
        high_dataframe = inputcsv.loc[(inputcsv['Host'] == i) & (inputcsv['Risk'] == 'High')]
        host_critcal = len(critical_dataframe.index)
        host_high = len(high_dataframe.index)
        if host_critcal != 0 or host_high != 0:
            analysis.hosts_vuln_count.update({i:{"Critical":host_critcal, "High":host_high}})

    analysis.hosts_vuln_count.update({"TOTAL":{"Critical":analysis.num_critical, "High":analysis.num_high}})

    return render_template('analysis.html', form=index.form, filename=index.filename, filtered=analysis.filtered, hosts=analysis.hosts, solutions=analysis.nested_solutions, risks=analysis.nested_risks, host_solutions=analysis.host_solutions, solutions_risk=analysis.solutions_risk, solutions_hosts=analysis.solutions_hosts, names=analysis.nested_name, name_list=analysis.names, solutions_list=analysis.solutions, count_data=count_data, count_hosts=count_hosts, count_vulns=count_vulns, hosts_vuln_count=analysis.hosts_vuln_count)


@app.route('/revalidate', methods=['POST', 'GET'])
def revalidate():
    clear_dir()
    if request.method == 'POST':
        before = request.files['beforeFileUpload']
        after = request.files['afterFileUpload']
        if before.filename == '' or after.filename == '':
            return redirect(request.url)
        elif before and not allowed_file(before.filename) or after and not allowed_file(after.filename):
            return redirect(request.url)
        elif before and allowed_file(before.filename) and after and allowed_file(after.filename):
            revalidate.before_filename = secure_filename(before.filename)
            revalidate.after_filename = secure_filename(after.filename)
            before.save(os.path.join(app.config['UPLOAD_PATH'], revalidate.before_filename))
            after.save(os.path.join(app.config['UPLOAD_PATH'], revalidate.after_filename))
            return redirect(url_for('validating'))
    else:
        return render_template('revalidation.html')


@app.route('/validating')
def validating():
    beforecsv = pd.read_csv(f"uploads/{revalidate.before_filename}", keep_default_na=False)
    replace(beforecsv)
    beforecsv = beforecsv.drop(beforecsv[beforecsv['Risk'] == 'None'].index)
    beforecsv = beforecsv.drop(beforecsv[beforecsv['Risk'] == 'Low'].index)
    beforecsv = beforecsv.drop(beforecsv[beforecsv['Risk'] == 'Log'].index)

    aftercsv = pd.read_csv(f"uploads/{revalidate.after_filename}", keep_default_na=False)
    replace(aftercsv)
    aftercsv = aftercsv.drop(aftercsv[aftercsv['Risk'] == 'None'].index)
    aftercsv = aftercsv.drop(aftercsv[aftercsv['Risk'] == 'Low'].index)
    aftercsv = aftercsv.drop(aftercsv[aftercsv['Risk'] == 'Log'].index)

    before_result = beforecsv.to_dict('records')
    after_result = aftercsv.to_dict('records')

    name_database = pd.read_csv("static/name_database.csv", keep_default_na=False)
    namedb = name_database.to_dict()
    # Cleaning empty values in the nested namedb dictionary
    drop_keys = lambda path, key, value: len(value) != 0
    cleandb = remap(namedb, visit=drop_keys)
    conversion_database = pd.read_csv("static/conversion.csv", keep_default_na=False)
    conversiondb = conversion_database.to_dict('records')

    before_filtered = []
    for i in before_result:
        if i['Risk'] != "None" and i['Risk'] != "Low":
            before_filtered.append(i)

    for i in before_filtered:
        for keys, values in cleandb.items():
            for k, v in values.items():
                if i['Name'] == v:
                    i['Name'] = keys

    getvals = operator.itemgetter('Host', 'Name')
    before_filtered.sort(key=getvals)
    res = []
    for k, g in itertools.groupby(before_filtered, getvals):
        res.append(next(g))
    before_filtered[:] = res

    for i in before_filtered:
        for j in conversiondb:
            if i['Name'] == j['Name']:
                i['Description'] = j['Description']
                i['Solution'] = j['Solution']

    after_filtered = []
    for i in after_result:
        if i['Risk'] != "None" and i['Risk'] != "Low":
            after_filtered.append(i)

    for i in after_filtered:
        for keys, values in cleandb.items():
            for k, v in values.items():
                if i['Name'] == v:
                    i['Name'] = keys

    getvals = operator.itemgetter('Host', 'Name')
    after_filtered.sort(key=getvals)
    res = []
    for k, g in itertools.groupby(after_filtered, getvals):
        res.append(next(g))
    after_filtered[:] = res

    for i in after_filtered:
        for j in conversiondb:
            if i['Name'] == j['Name']:
                i['Description'] = j['Description']
                i['Solution'] = j['Solution']

    after_df = pd.DataFrame(after_filtered)
    before_df = pd.DataFrame(before_filtered)
    r_vuln = after_df[after_df['Name'].isin(before_df['Name'])]
    remaining_vuln = r_vuln.to_dict('records')
    new_vulns = after_df[~after_df['Name'].isin(before_df['Name'])]
    mitigated_vuln = beforecsv.merge(aftercsv.drop_duplicates(), on=['Name', 'Host'], how='left', indicator=True)
    mitigated_vuln = mitigated_vuln[mitigated_vuln['_merge'] == 'left_only']

    hosts = []
    for i in remaining_vuln:
        if i not in hosts:
            hosts.append(i['Host'])
    hosts.sort()

    solutions = []
    for i in remaining_vuln:
        if i['Solution'] not in solutions:
            solutions.append(i['Solution'])

    names = []
    for i in remaining_vuln:
        if i['Name'] not in names:
            names.append(i['Name'])

    host_solutions = {}
    for i in remaining_vuln:
        if i['Host'] not in host_solutions:
            host_solutions[i['Host']] = [i['Solution']]
        if i['Solution'] not in host_solutions[i['Host']]:
            host_solutions[i['Host']].append(i['Solution'])

    for keys, values in host_solutions.items():
        values = list(set(values))
        host_solutions.update({keys:values})

    solutions_hosts = {}
    for i in remaining_vuln:
        if i['Solution'] not in solutions_hosts:
            solutions_hosts[i['Solution']] = [i['Host']]
        if i['Host'] not in solutions_hosts[i['Solution']]:
            solutions_hosts[i['Solution']].append(i['Host'])

    for keys, values in solutions_hosts.items():
        values = list(set(values))
        solutions_hosts.update({keys:values})

    solutions_risk = {}
    for i in remaining_vuln:
        if i['Solution'] not in solutions_risk:
            solutions_risk[i['Solution']] = [i['Risk']]
        if i['Risk'] not in solutions_risk[i['Solution']]:
            solutions_risk[i['Solution']].append(i['Risk'])

    for keys, values in solutions_risk.items():
        if 'Critical' in values:
            values = ['Critical']
        if 'High' in values:
            values = ['High']
        solutions_risk.update({keys:values})


    nested_solutions = {k: f.groupby('Risk')['Description'].apply(list).to_dict() for k, f in r_vuln.groupby('Solution')}

    for main_keys, main_values in nested_solutions.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    nested_risks = {k: f.groupby('Solution')['Description'].apply(list).to_dict() for k, f in r_vuln.groupby('Risk')}

    for main_keys, main_values in nested_risks.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    nested_name = {k: f.groupby('Solution')['Host'].apply(list).to_dict() for k, f in r_vuln.groupby('Name')}

    for main_keys, main_values in nested_risks.items():
        for keys, values in main_values.items():
            values = list(set(values))
            main_values.update({keys:values})

    # Graphs

    before_critical_count = 0
    before_high_count = 0
    before_mediun_count = 0

    after_critical_count = 0
    after_high_count = 0
    after_mediun_count = 0

    if 'Critical' in beforecsv['Risk'].values:
        before_critical_count = beforecsv['Risk'].value_counts()['Critical']
    if 'High' in beforecsv['Risk'].values:
        before_high_count = beforecsv['Risk'].value_counts()['High']
    if 'Medium' in beforecsv['Risk'].values:
        before_mediun_count = beforecsv['Risk'].value_counts()['Medium']

    if 'Critical' in aftercsv['Risk'].values:
        after_critical_count = aftercsv['Risk'].value_counts()['Critical']
    if 'High' in aftercsv['Risk'].values:
        after_high_count = aftercsv['Risk'].value_counts()['High']
    if 'Medium' in aftercsv['Risk'].values:
        after_mediun_count = aftercsv['Risk'].value_counts()['Medium']

    labels = ["Before", "After"]
    critical_data =  [before_critical_count, after_critical_count]
    high_data = [before_high_count, after_high_count]
    medium_data = [before_mediun_count, after_mediun_count]

    after_count = len(aftercsv.index)
    mitigated = len(mitigated_vuln)

    piechart_data = [
        ('Mitigated', mitigated),
        ('Not Mitigated', after_count),
    ]

    piechart_labels = [row[0] for row in piechart_data]
    piechart_values = [row[1] for row in piechart_data]

    return render_template('validation.html', before_filename=revalidate.before_filename, after_filename=revalidate.after_filename, before=before_filtered, after=after_filtered, remaining_vuln=remaining_vuln, hosts=hosts, solutions_list=solutions, solutions=nested_solutions, risks=nested_risks, host_solutions=host_solutions, solutions_risk=solutions_risk, solutions_hosts=solutions_hosts, names=nested_name, name_list=names, labels=labels, critical_data=critical_data, high_data=high_data, medium_data=medium_data, piechart_labels=piechart_labels, piechart_values=piechart_values, new_vulns=new_vulns)


@app.route('/resources')
def resources():
    googleresults = {}
    for x in analysis.solutions:
        googletitle = []
        query = "how to " + x
        searchres = search(query, tld="com", num=5, stop=5, pause=2)
        for i in searchres:
            reqs = requests.get(i)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            title = soup.find_all('title')
            if len(title) > 0:
                googletitle.append({title[0].get_text().strip():i})
            else:
                googletitle.append({i:i})
        googleresults.update({x:googletitle})

    return render_template('resources.html', solutions=analysis.solutions, googleresults=googleresults)


@app.route('/report', methods=['POST', 'GET'])
def report():
    if request.method == 'POST':
        if request.form['companyname'] != '' and request.form['startdate'] != '' and request.form['enddate'] != '':
            form = ReportForm(request.form)
            if form.validate_on_submit(form):
                fn = os.path.splitext(index.filename)[0]
                companyname = html.escape(request.form['companyname'], quote=True)
                companyabbv = html.escape(request.form['companyabbv'], quote=True)
                startdate = request.form['startdate']
                enddate = request.form['enddate']
                start_date = datetime.datetime.strptime(startdate, dateformat)
                start_date = start_date.strftime('%d %b %Y')
                end_date = datetime.datetime.strptime(enddate, dateformat)
                end_date = end_date.strftime('%d %b %Y')
                num_hosts = len(analysis.hosts)
                num_critical = analysis.num_critical
                num_high = analysis.num_high
                html_file = render_template('report.html', filename=index.filename,  filtered=analysis.filtered, name_list=analysis.names, names=analysis.nested_name, solutions_list=analysis.solutions,hosts=analysis.hosts, solutions_hosts=analysis.solutions_hosts, solutions=analysis.nested_solutions, risks=analysis.nested_risks, host_solutions=analysis.host_solutions, solutions_risk=analysis.solutions_risk, hosts_vuln_count=analysis.hosts_vuln_count, companyname=companyname, companyabbv=companyabbv, startdate=start_date, enddate=end_date, numhosts=num_hosts, num_critical=num_critical, num_high=num_high)
                pdfkit.from_string(html_file, r"./uploads/out.pdf", configuration=config)
                parse(pdf_file=r"uploads/out.pdf", docx_file=r"uploads/output.docx", start=0, end=None)
                docx = r"uploads/output.docx"
                download_file = open(docx, 'rb')
                response = make_response(download_file)
                response.headers["Content-Type"] = "application/force-download"
                response.headers['Content-Disposition'] = "attachment; filename="+fn+".docx"
                return response
            else:
                return redirect(url_for('analysis'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/guides')
def guides():
    return render_template('guides.html')


@app.route('/scripts')
def scripts():
    return render_template('scripts.html')


@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    global SITE_NAME
    if request.method == 'GET':
        resp = requests.get(f"{SITE_NAME}{path}")
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == 'POST':
        resp = requests.post(f"{SITE_NAME}{path}", data=request.form)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port='5002', debug=True)
    app.run(host='0.0.0.0', port='8000', debug=False, ssl_context=('cert.pem', 'key.pem'))
