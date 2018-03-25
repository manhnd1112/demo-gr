from django.shortcuts import render
from django.http import JsonResponse
import json
import numpy as np
from   scipy import optimize 
from .form import UploadFileForm
import json
import os, errno
from django.conf import settings

# Create your views here.
import xlrd, os
class Views:


    def handle_uploaded_file(f):
        workbook = xlrd.open_workbook(file_contents=f.read())
        sheet = workbook.sheet_by_index(0)
        nrows = sheet.nrows - 1
        ncols = sheet.ncols
        data = []
        for col in range(sheet.ncols):
            data.append(sheet.col_values(col))
        for i in range(len(data)):
            data[i].remove(data[i][0])
        print(data)
        return data
    
    def index(request):
        if request.method == 'POST':
            file_input = request.FILES['file']
            data = Views.handle_uploaded_file(file_input)
            return render(request, "main/index.html", {'data': data, 'file_input_name': file_input.name.split('.')[0]})
        else:
            return render(request, "main/index.html", {'data': ''})
class Funcs: 
    def init(AT, X, Y , n, buggest, AC_PV):
        for i in range(n):
            AT[i] = (i+1)*1.0
            X[i] = (i + 1)/(n*1.0)
            Y[i] = AC_PV[i]/(buggest*1.0)
        
    # for gomperzt
    def gomperzt_func(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        y = parameters[2]
        return a * np.exp(-np.exp(b - y*xdata))

    # for logistic
    def logistic_func(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        y = parameters[2]
        return a / (1 + np.exp(b - y*xdata))

    # for logistic
    def bass_func(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        y = parameters[2]
        return a * ( ( 1 - np.exp(-(b + y)*xdata) ) / ( ( 1 + (y / b)*np.exp(-(b + y)*xdata) ) ) )

    # for logistic
    def weibull_func(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        y = parameters[2]
        return a * (1 - np.exp( -( xdata / y )**b ))

    #log-logistic
    def log_logistic_func(parameters,xdata):
        a = parameters[0]
        b = parameters[1]
        return ( (xdata/a)**b ) / ( 1 + (xdata/a)**b )        

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
        ES = Funcs.getES(AT , PV, EV_PV, evaluationPoint)
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
        SV = Funcs.getSV(PV, EV_PV, evaluationPoint)
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

    def getCI(CPI, w_cpi, SPI, w_spi):
        return CPI*w_cpi + SPI*w_spi

    def getCIt(CPI, w_cpi, SPIt, w_spit):
        return CPI*w_cpi + SPIt*w_spit

    # EAC caculated by EVM
    def getEAC(AC_PV, EV_PV, BAC, evaluationPoint, PF):
        return round(AC_PV[evaluationPoint -1] + (BAC - EV_PV[evaluationPoint -1])/PF, 2)
    
    def getEACGM(AC_PV, xdata, evaluationPoint, growModel, parametersEstimated, BAC, index = 1.0):
        if(growModel == 'gompertz'):
            restBudget = (Funcs.gomperzt_func(parametersEstimated, index) - Funcs.gomperzt_func(parametersEstimated, xdata[evaluationPoint -1]))*BAC
        elif(growModel == 'logistic'):
            restBudget = (Funcs.logistic_func(parametersEstimated, index) - Funcs.logistic_func(parametersEstimated, xdata[evaluationPoint -1]))*BAC
        elif(growModel == 'bass'):
            restBudget = (Funcs.bass_func(parametersEstimated, index) - Funcs.bass_func(parametersEstimated, xdata[evaluationPoint -1]))*BAC
        elif(growModel == 'log_logistic'):
            restBudget = (Funcs.log_logistic_func(parametersEstimated, index) - Funcs.log_logistic_func(parametersEstimated, xdata[evaluationPoint -1]))*BAC
        else:
            restBudget = (Funcs.weibull_func(parametersEstimated, index) - Funcs.weibull_func(parametersEstimated, xdata[evaluationPoint -1]))*BAC            
        
        return round(AC_PV[evaluationPoint - 1] + restBudget, 2)

    def optimizeLeastSquares(growModel, xdata, ydata, method = 'dogbox'):
        x0 = [0.1, 0.2, 0.3] 
        print(growModel)
        if(growModel == 'gompertz'):
            OptimizeResult  = optimize.least_squares(Funcs.residuals,  x0,method = method,
                                          args   = ( xdata, ydata,Funcs.gomperzt_func) )
        elif(growModel == 'logistic'):
            OptimizeResult  = optimize.least_squares(Funcs.residuals,  x0,method = method,
                                          args   = ( xdata, ydata,Funcs.logistic_func) )
        elif(growModel == 'bass'):
            OptimizeResult  = optimize.least_squares(Funcs.residuals,  x0,method = method,
                                          args   = ( xdata, ydata,Funcs.bass_func) )
        elif(growModel == 'log_logistic'):
            x0 = [0.1, 0.2]
            OptimizeResult  = optimize.least_squares(Funcs.residuals,  x0,method = method,
                                          args   = ( xdata, ydata,Funcs.log_logistic_func) )
        else:
            OptimizeResult  = optimize.least_squares(Funcs.residuals,  x0,method = method,
                                          args   = ( xdata, ydata,Funcs.weibull_func) )

        parametersEstimated = OptimizeResult.x
        return parametersEstimated

class MyIO:
    
    def writeResultToFile(project_name, grow_model, evaluation_time, data):
        static_dir = settings.STATICFILES_DIRS[0]

        #Creating a folder in static directory
        new_pro_dir_path = os.path.join(static_dir,'%s'%(project_name))
        new_pro_gro_dir_path = os.path.join(static_dir,'%s/%s'%(project_name, grow_model))
        new_pro_gro_eva_dir_path = os.path.join(static_dir, '%s/%s/%s'%(project_name, grow_model, evaluation_time))
        result_file_path = os.path.join(static_dir, '%s/%s/%s/data.json'%(project_name, grow_model, evaluation_time))

        if not os.path.exists(new_pro_dir_path):
            os.makedirs(new_pro_dir_path)

        if not os.path.exists(new_pro_gro_dir_path):
            os.makedirs(new_pro_gro_dir_path)
        
        if not os.path.exists(new_pro_gro_eva_dir_path):
            os.makedirs(new_pro_gro_eva_dir_path)
        
        with open(result_file_path, 'w') as f:
            json.dump(data, f)

class Ajax:
    def test(request):
        project_name = request.GET.get('project_name')
        pd = int(request.GET.get('pd'))
        budget = float(request.GET.get('budget'))
        data = json.loads(request.GET.get('data'))
        grow_model = request.GET.get('growModel')
        evaluationPoint = int(request.GET.get('evaluationPoint'))
        evaluation_percent = int(request.GET.get('evaluation_percent'))
        AC = float(request.GET.get('AC'))
        print(project_name)
        print(evaluation_percent)

        PV = data[1]
        EV_PV = data[2]
        AC_PV = data[3]
        AT = np.zeros(pd)
        xdata = np.zeros(pd)
        ydata = np.zeros(pd)

        Funcs.init(AT, xdata, ydata, pd, budget, AC_PV)                
        ES = Funcs.getES(AT, PV, EV_PV, evaluationPoint)
        SPI = Funcs.getSPI(PV, EV_PV, evaluationPoint)
        CPI = Funcs.getCPI(EV_PV, AC_PV, evaluationPoint)
        SPIt = Funcs.getSPIt(AT, PV, EV_PV, evaluationPoint)
        SCI = Funcs.getSCI(SPI, CPI)
        SCIt = Funcs.getSCIt(SPIt, CPI)
        TV = Funcs.getTV(budget, pd, PV, EV_PV, evaluationPoint)
        ED = Funcs.getED(AT, SPI, evaluationPoint)

        EACtPV1 = Funcs.getEACtPV1(pd, Funcs.getTV(budget, pd, PV, EV_PV, evaluationPoint))
        EACtPV2 = Funcs.getEACtPV2(pd, SPI)
        EACtPV3 = Funcs.getEACtPV3(pd, SCI)        

        EACtED1 = Funcs.getEACtED(pd, AT, ED, 1, evaluationPoint)
        EACtED2 = Funcs.getEACtED(pd, AT, ED, SPI, evaluationPoint)
        EACtED3 = Funcs.getEACtED(pd, AT, ED, SCI, evaluationPoint)
        
        EACtES1 = Funcs.getEACtES(pd, AT, ES, 1, evaluationPoint)
        EACtES2 = Funcs.getEACtES(pd, AT, ES, SPIt, evaluationPoint)
        EACtES3 = Funcs.getEACtES(pd, AT, ES, SCIt, evaluationPoint)

        EAC1 = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, 1)
        EAC2 = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, CPI)
        EAC3_SPI = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, SPI)
        EAC3_SPIt = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, SPIt)
        EAC4_SCI = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, SCI)
        EAC4_SCIt = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, SCIt)
        
        CI = Funcs.getCI(CPI, 0.8, SPI, 0.2)
        CIt = Funcs.getCIt(CPI, 0.8, SPIt, 0.2)
        EAC5_CI = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, CI)
        EAC5_CIt = Funcs.getEAC(AC_PV, EV_PV, budget, evaluationPoint, CIt)
        
        # print(xdata)
        # print(ydata)
        lb = [0,0,0]
        ub = [2,2,2]

        parametersEstimated = Funcs.optimizeLeastSquares(grow_model, xdata, ydata)
        EAC_GM1 = Funcs.getEACGM(AC_PV, xdata, evaluationPoint, grow_model, parametersEstimated, budget, 1.0)
        EAC_GM2 = Funcs.getEACGM(AC_PV, xdata, evaluationPoint, grow_model, parametersEstimated, budget, 1.0/SPIt)

        data = {
            'status': 'ok',
            'alpha': parametersEstimated[0],
            'beta': parametersEstimated[1],
            'gamma': '',
            'ES': ES,
            'SPI': SPI,
            'CPI': CPI, 
            'SPIt': SPIt,
            'SCI': SCI,
            'SCIt': SCIt, 
            'TV': TV, 
            'ED': ED,
            'EACtPV1': EACtPV1,
            'EACtPV2': EACtPV2,
            'EACtPV3': EACtPV3,
            'EACtED1': EACtED1,
            'EACtED2': EACtED2,
            'EACtED3': EACtED3,
            'EACtES1': EACtES1,
            'EACtES2': EACtES2,
            'EACtES3': EACtES3,
            'EAC1': EAC1,
            'EAC2': EAC2,
            'EAC3_SPI': EAC3_SPI,
            'EAC3_SPIt': EAC3_SPIt,
            'EAC4_SCI': EAC4_SCI,
            'EAC4_SCIt': EAC4_SCIt,
            'EAC5_CI': EAC5_CI,
            'EAC5_CIt': EAC5_CIt,
            'EAC_GM1': EAC_GM1,
            'EAC_GM2': EAC_GM2
        }

        results_data = {
            'AC': AC,
            'EAC1': EAC1,
            'EAC2': EAC2,
            'EAC3_SPI': EAC3_SPI,
            'EAC3_SPIt': EAC3_SPIt,
            'EAC4_SCI': EAC4_SCI,
            'EAC4_SCIt': EAC4_SCIt,
            'EAC5_CI': EAC5_CI,
            'EAC5_CIt': EAC5_CIt,
            'EAC_GM1': EAC_GM1,
            'EAC_GM2': EAC_GM2
        }
        MyIO.writeResultToFile(project_name, grow_model, evaluation_percent, results_data)
        return JsonResponse(data)
    
    def mape(request): 
        results_dir = settings.STATICFILES_DIRS[0]
        list_projects = os.listdir(results_dir)
        for pro_name in list_projects:
            pro_dir =  os.path.join(results_dir,'%s'%(pro_name))
            print(os.listdir(pro_dir))
        return JsonResponse({'data': ''})

    