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
        for col in range(sheet.ncols):
            data.append(sheet.col_values(col))
        for i in range(len(data)):
            data[i].remove(data[i][0])
        return render(request, "main/index.html", {'data': data})

class Ajax:
    def init(AT, X, Y , n, buggest, AC_PV):
        for i in range(n):
            AT[i] = (i+1)*1.0
            X[i] = (i + 1)/(n*1.0)
            Y[i] = AC_PV[i]/(buggest*1.0)
        
    # for gomperzt
    def exp_decay(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        c = parameters[2]
        return a * np.exp(-np.exp(b - c*xdata))

    #Compute residuals of y_predicted - y_observed    
    def residuals(parameters,x_data,y_observed,func):    
        return func(parameters,x_data) - y_observed

    def getES(AT , PV, EV_PV, evaluationPoint):
        # example: evaluationPoint = 9 -> current EV is: EV[8]. i = 0..8
        EV = EV_PV[evaluationPoint-1]
        t = [ n for n,i in enumerate(PV) if i>EV ][0] - 1
        #print(PV[t_1], EV)
        #print(t_1, t_1 - 1)
        return round(AT[t] + (EV - PV[t])/(PV[t+1] - PV[t]), 2)
    
    def getSPI(PV, EV_PV, evaluationPoint):
        return round(EV_PV[evaluationPoint -1]/PV[evaluationPoint - 1], 2) 

    def getCPI(EV_PV, AC_PV, evaluationPoint):
        return round(EV_PV[evaluationPoint -1]/AC_PV[evaluationPoint - 1], 2)

    def getSPIt(AT , PV, EV_PV, evaluationPoint):
        ES = Ajax.getES(AT , PV, EV_PV, evaluationPoint)
        return round(ES/AT[evaluationPoint - 1], 2)
    
    def getSCI(SPI, CPI):
        return round(SPI*CPI, 2)
    
    def getSCIt(SPIt, CPI):
        return round(SPIt*CPI, 2)
    
    def getED(AT, SPI, evaluationPoint):
        return round(AT[evaluationPoint -1]*SPI, 2)

    def getSV(PV, EV_PV, evaluationPoint):
        return EV_PV[evaluationPoint -1] - PV[evaluationPoint -1]

    def getTV(BAC, PD, PV, EV_PV, evaluationPoint):
        PVrate = BAC/PD
        SV = Ajax.getSV(PV, EV_PV, evaluationPoint)
        return round(SV/PVrate, 2)

    def getEACtPV1(PD, TV):
        return PD - TV
    
    def getEACtPV2(PD, SPI):
        return round(PD/SPI, 2)

    def getEACtPV3(PD, SCI):
        return round(PD/SCI, 2)   

    # return EACt caculated by ED
    def getEACtED(PD, AT, ED, PF, evaluationPoint):
        return round(AT[evaluationPoint -1] + (max(PD, AT[evaluationPoint -1]) - ED)/PF, 2)

     # return EACt caculated by ES
    def getEACtES(PD, AT, ES, PF, evaluationPoint):
        return round(AT[evaluationPoint -1] + (PD - ES)/PF, 2)

    def test(request):
        pd = int(request.GET.get('pd'))
        budget = float(request.GET.get('budget'))
        data = json.loads(request.GET.get('data'))
        evaluationPoint = int(request.GET.get('evaluationPoint'))
        PV = data[1]
        EV_PV = data[2]
        AC_PV = data[3]
        AT = np.zeros(pd)
        xdata = np.zeros(pd)
        ydata = np.zeros(pd)

        Ajax.init(AT, xdata, ydata, pd, budget, AC_PV)                
        ES = Ajax.getES(AT, PV, EV_PV, evaluationPoint)
        SPI = Ajax.getSPI(PV, EV_PV, evaluationPoint)
        CPI = Ajax.getCPI(EV_PV, AC_PV, evaluationPoint)
        SPIt = Ajax.getSPIt(AT, PV, EV_PV, evaluationPoint)
        SCI = Ajax.getSCI(SPI, CPI)
        SCIt = Ajax.getSCIt(SPIt, CPI)
        ED = Ajax.getED(AT, SPI, evaluationPoint)

        EACtPV1 = Ajax.getEACtPV1(pd, Ajax.getTV(budget, pd, PV, EV_PV, evaluationPoint))
        EACtPV2 = Ajax.getEACtPV2(pd, SPI)
        EACtPV3 = Ajax.getEACtPV3(pd, SCI)        

        EACtED1 = Ajax.getEACtED(pd, AT, ED, 1, evaluationPoint)
        EACtED2 = Ajax.getEACtED(pd, AT, ED, SPI, evaluationPoint)
        EACtED3 = Ajax.getEACtED(pd, AT, ED, SCI, evaluationPoint)
        
        EACtES1 = Ajax.getEACtES(pd, AT, ES, 1, evaluationPoint)
        EACtES2 = Ajax.getEACtES(pd, AT, ES, SPIt, evaluationPoint)
        EACtES3 = Ajax.getEACtES(pd, AT, ES, SCIt, evaluationPoint)

        print(ES, SPI, CPI, SPIt, SCI, SCIt, ED)

        # print(xdata)
        # print(ydata)
        x0 = [0, 0, 0] 
        lb = [0,0,0]
        ub = [2,2,2]
        OptimizeResult  = optimize.least_squares(Ajax.residuals,  x0,method = 'dogbox',
                                          args   = ( xdata, ydata,Ajax.exp_decay) )
        parametersEstimated = OptimizeResult.x
        data = {
            'status': 'ok',
            'alpha': parametersEstimated[0],
            'beta': parametersEstimated[1],
            'gamma': parametersEstimated[2],
            'ES': ES,
            'SPI': SPI,
            'CPI': CPI, 
            'SPIt': SPIt,
            'SCI': SCI,
            'SCIt': SCIt, 
            'ED': ED,
            'EACtPV1': EACtPV1,
            'EACtPV2': EACtPV2,
            'EACtPV3': EACtPV3,
            'EACtED1': EACtED1,
            'EACtED2': EACtED2,
            'EACtED3': EACtED3,
            'EACtES1': EACtES1,
            'EACtES2': EACtES2,
            'EACtES3': EACtES3
        }
        return JsonResponse(data)