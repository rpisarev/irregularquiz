#!/usr/bin/env python
# -*- mode:python; coding:utf-8; -*-
# author: Ruslan Pisarev

import os
import random
from json import dumps
from sqlite3 import connect
from bottle import route, run, request, redirect


@route('/')
def main_page_irregular():
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        "template/main.html")).read()


@route('/en/irregular/verb')
def irr_page_open():
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        "template/irregular_verb.html")).read()


@route('/contacts')
def contacts():
    return redirect('/')


def check_verb(verb, sample):
    return any([verb == v.strip() for v in sample.split(",")])


def gen_correct_tr(correct_verbs, user_verbs, rights):
    tr = """<tr>\n<td>{}</td>\n<td>{}</td>\n<td>{}</td>\n</tr>\n"""
    tds = []
    for x in xrange(3):
        if rights[x]:
            content = """<span style="color:green">{}</span>""".format(user_verbs[x])
        else:
            content = """<span style="color:red">{}</span>
            <br><span style="color:blue">{}</span>""".format(
                user_verbs[x], correct_verbs[x])
        tds.append(content)
    return tr.format(tds[0], tds[1], tds[2])


@route('/check/en/irregular_verb', method='POST')
def check_irregular_verb():
    position = int(request.forms.get("position"))
    num = request.forms.get("verbid")
    input1 = request.forms.get("input1")
    input2 = request.forms.get("input2")
    main = request.forms.get("main")
    sqlite_connect = connect(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                          "irregular_verb_en.db"))
    c = sqlite_connect.cursor()
    query = "select `infinitive`, `past_simple`, `past_participle` from irregular where id={}"
    c.execute(query.format(num))
    res = c.fetchall()[0]
    c.close()
    user_verbs = []
    if position == 0:
        first = True
        user_verbs.append(main)
    else:
        first = check_verb(input1, res[0])
        user_verbs.append(input1)
    if position == 1:
        user_verbs.append(main)
        second = True
    elif position == 0:
        second = check_verb(input1, res[1])
        user_verbs.append(input1)
    else:
        second = check_verb(input2, res[1])
        user_verbs.append(input2)
    if position == 2:
        third = True
        user_verbs.append(main)
    else:
        third = check_verb(input2, res[2])
        user_verbs.append(input2)
    verbs_correct = (first, second, third)
    checkpoints = len([v for v in verbs_correct if v]) - 1
    tr = gen_correct_tr(res, user_verbs, verbs_correct)

    return  dumps({"tr": tr + create_quiz_tr(),
                  "checkpoints": checkpoints})


@route('/start/en/irregular_verb', method='POST')
def start_irregular_verb():
    return create_quiz_tr()


def irregular(infinitive, kind, forms):
    return "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        infinitive, forms[0], forms[1])


def choice_verb(position):
    verb_form = {0: "infinitive",
                 1: "past_simple",
                 2: "past_participle"}[position]
    verb_number = random.choice(xrange(188))
    sqlite_connect = connect(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                          "irregular_verb_en.db"))
    c = sqlite_connect.cursor()
    query = "select `{}` from irregular where id = {}"
    c.execute(query.format(verb_form, verb_number))
    res = c.fetchall()[0][0]
    c.close()
    return res.split(",")[random.choice(xrange(2))] if "," in res else res, verb_number


def create_quiz_tr():
    position = random.choice(xrange(3))
    verb, num = choice_verb(position)
    tr = """<tr data-position="{}">\n<td>{}</td>\n<td>{}</td>\n<td>{}</td>\n</tr>\n"""
    tds = []
    input_count = 1
    for td in xrange(3):
        if td == position:
            content = """<span id="main_value" data-num="{}">{}</span>""".format(
                num, verb)
        else:
            content = """<input type="text" size="20" id="input{}">""".format(
                input_count)
            input_count += 1
        tds.append(content)
    return tr.format(position, tds[0], tds[1], tds[2])


run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
