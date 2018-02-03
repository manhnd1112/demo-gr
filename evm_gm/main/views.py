from django.shortcuts import render
from django.http import JsonResponse
import json
import numpy as np
from   scipy import optimize 
# Create your views here.
import xlrd, os
class Views:
    def index(request):
        file_location = os.getcwd() + "/main/static/data/Project1.xls"
        workbook = xlrd.open_workbook(file_location)
        sheet = workbook.sheet_by_index(0)
        nrows = sheet.nrows - 1
        ncols = sheet.ncols
        data = []
        print(nrows, ncols)
        for col in range(sheet.ncols):
            data.append(sheet.col_values(col))
        for i in range(len(data)):
            data[i].remove(data[i][0])
        return render(request, "main/index.html", {'data': data})

class Ajax:
    def init(X, Y , n, buggest, dataArr):
        for i in range(len(dataArr)):
            X[i] = (i + 1)/(n*1.0)
            Y[i] = dataArr[i]/(buggest*1.0)
        
    # for gomperzt
    def exp_decay(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        c = parameters[2]
        return a * np.exp(-np.exp(b - c*xdata))

    #Compute residuals of y_predicted - y_observed    
    def residuals(parameters,x_data,y_observed,func):    
        return func(parameters,x_data) - y_observed

    def test(request):
        data = json.loads(request.GET.get('data'))
        pd = int(request.GET.get('pd'))
        budget = float(request.GET.get('budget'))
        print(data, pd, budget)
        xdata = np.zeros(len(data[3]))
        ydata = np.zeros(len(data[3]))
        Ajax.init(xdata, ydata, pd, budget, data[3])
        x0 = [1, 1, 1] 
        lb = [0,0,0]
        ub = [2,2,2]
        OptimizeResult  = optimize.least_squares(Ajax.residuals,  x0, method = 'dogbox',
                                          args   = ( xdata, ydata,Ajax.exp_decay) )
        parametersEstimated = OptimizeResult.x
        data = {
            'status': 'ok',
            'alpha': parametersEstimated[0],
            'beta': parametersEstimated[1],
            'gamma': parametersEstimated[2]
        }
        return JsonResponse(data)