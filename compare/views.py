from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from upload.models import ExcelFilePair
import os
from django.conf import settings
import pandas as pd
import itertools


# Create your views here.


def get_values(file, filter):
    df = get_df(file)
    col_list = filter.split(' ➤ ')
    coldict, skip_rows = fill_cols(df)
    values = []
    col_index = -1
    if skip_rows == 0:
        values = list(df[filter])
    else:
        print(f'{file.name}: {coldict}')
        for i in range(len(df.columns)):
            flag = True
            back_counter = -1
            for j in range(len(coldict[i + 1]) - 1):
                print(f'{file.name}: checking for {coldict[i + 1][-j - 1]} != null')
                if coldict[i + 1][-j - 1] != '':
                    print(f'{file.name}: checking for {coldict[i + 1][-j - 1]} != {col_list[back_counter]}')
                    if coldict[i + 1][-j - 1] != col_list[back_counter]:
                        flag = False
                        break
                    back_counter -= 1
                # print(f'checking for {coldict[i+1][-j-1]} != {df.loc[df.index[skip_rows-j-1]][i]}')
                # if coldict[i+1][-j-1] != df.loc[df.index[skip_rows-j-1]][i]:
                #     flag = False
                #     break
            if flag == True:
                print(
                    f'{file.name}: checking for {coldict[i + 1][0]} == {col_list[0]} or Unnamed in {coldict[i + 1][0]}')
                if coldict[i + 1][0] == col_list[0] or 'Unnamed:' in coldict[i + 1][0]:
                    print(f'{col_list[0]}: index: {i}')
                    col_index = i
                    break
        values = list(df[df.columns[col_index]][skip_rows:])
    return values
    # delete_file_pair(file_pair, file1path, file2path)


def delete_file_pair(file_pair, fp1, fp2):
    file_pair.delete()
    os.remove(fp1)
    os.remove(fp2)


def display_table(request):
    file_pair = ExcelFilePair.objects.last()
    context = {}
    file1 = file_pair.file1
    file2 = file_pair.file2
    file1name = os.path.basename(file1.name)
    file2name = os.path.basename(file2.name)
    name1 = file1name.split('.')[0]
    name2 = file2name.split('.')[0]
    if len(name1) >= 16:
        name1 = name1[:16]
    if len(name2) >= 16:
        name2 = name2[:16]
    dd1 = render_dropdown(file1)
    dd2 = render_dropdown(file2)
    context['name1'] = name1
    context['name2'] = name2
    context['dd1'] = dd1
    context['dd2'] = dd2
    context['display'] = False
    context['select1'] = dd1[0]
    context['select2'] = dd2[0]
    context['pivot_file_name'] = None
    context['selectp'] = 'Pivot Not Required'
    context['selectf'] = 'View All'
    if request.method == 'POST':
        dictionary = request.POST
        filter1 = dictionary.get('field1')
        filter2 = dictionary.get('field2')
        view_filter = dictionary.get('view filter')
        pivot = dictionary.get('pivot')

        if pivot == 'Pivot Not Required':
            pivot_column = pivot
            pivot_values = None
            pivot_file_name = None
        else:
            pivot_column = pivot[9:]
            pivot_file_name = pivot[1:7]
            if pivot_file_name == 'File-1':
                pivot_file = file1
            else:
                pivot_file = file2
            pivot_values = get_values(pivot_file, pivot_column)
        values1 = get_values(file1, filter1)
        values2 = get_values(file2, filter2)
        a = []
        b = []
        c = []
        if pivot == 'Pivot Not Required':
            if view_filter == 'View Unique':
                for v1, v2 in itertools.zip_longest(values1, values2, fillvalue=''):
                    if v1 != v2:
                        a.append(v1)
                        b.append(v2)
                values1, values2 = a, b
            elif view_filter == 'View Same':
                for v1, v2 in itertools.zip_longest(values1, values2, fillvalue=''):
                    if v1 == v2:
                        a.append(v1)
                        b.append(v2)
                values1, values2 = a, b
        if pivot != 'Pivot Not Required':
            if view_filter == 'View Unique':
                for v1, v2, p in itertools.zip_longest(values1, values2, pivot_values, fillvalue=''):
                    if v1 != v2:
                        a.append(v1)
                        b.append(v2)
                        c.append(p)
                values1, values2, pivot_values = a, b, c
            elif view_filter == 'View Same':
                for v1, v2, p in itertools.zip_longest(values1, values2, pivot_values, fillvalue=''):
                    if v1 == v2:
                        a.append(v1)
                        b.append(v2)
                        c.append(p)
                values1, values2, pivot_values = a, b, c
        #context['view_filter']
        context['select1'] = filter1
        context['select2'] = filter2
        context['selectp'] = pivot_column
        context['selectf'] = view_filter
        context['pivot_column'] = pivot_column
        context['display'] = True
        context['filter1'] = filter1
        context['filter2'] = filter2
        context['pivot_file_name'] = pivot_file_name
        if pivot_column != 'Pivot Not Required':
            context['zipper'] = itertools.zip_longest(values1, values2, pivot_values, fillvalue='')
        else:
            context['zipper'] = itertools.zip_longest(values1, values2, fillvalue='')
    return render(request, 'compare/filters.html', context)


def get_df(file):
    filepath = os.path.join(settings.MEDIA_ROOT, file.name)
    ext = file.name.split('.')[-1]
    if ext == 'csv':
        df = pd.read_csv(filepath).dropna(how='all', axis=1).dropna(how='all', axis=0).fillna('')
    elif ext == 'tsv':
        df = pd.read_csv(filepath, sep='\t').dropna(how='all', axis=1).dropna(how='all', axis=0).fillna('')
    else:
        df = pd.read_excel(filepath).dropna(how='all', axis=1).dropna(how='all', axis=0).fillna('')
    df = df.applymap(str)
    df.columns = df.columns.astype(str)
    return df


def render_dropdown(file):
    df = get_df(file)
    coldict = fill_cols(df)[0]
    dd_fields = []
    for key in coldict:
        buff = ''
        for field in coldict[key]:
            if field != '' and 'Unnamed:' not in field:
                if buff == '':
                    buff += field
                else:
                    buff += ' ➤ '
                    buff += field
        dd_fields.append(buff)
    return dd_fields


def col_check(coldict):
    for num in coldict:
        if len(set(coldict[num])) < 1:
            return False
        if len(set(coldict[num])) == 1 and (coldict[num][0] == '' or 'Unnamed:' in coldict[num][0]):
            return False
        if len(set(coldict[num])) == 2 and (coldict[num][0] == '' or coldict[num][1] == '') and (
                'Unnamed:' in coldict[num][0] or 'Unnamed:' in coldict[num][1]):
            return False
    return True


def fill_cols(df):
    coldict = {}
    skip_rows = 0
    for j in range(len(df.columns)):
        coldict[j + 1] = [df.columns[j]]
        # if not 'Unnamed:' in df.columns[j]:
        #     coldict[j + 1] = [df.columns[j]]
        # else:
        #     coldict[j + 1] = []
    if col_check(coldict):
        return coldict, skip_rows
    else:
        for i in range(len(df)):
            for j in range(len(df.columns)):
                coldict[j + 1].append(df.loc[df.index[i]][df.columns[j]])
            skip_rows += 1
            if col_check(coldict):
                return coldict, skip_rows
