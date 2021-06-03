import ROOT
from ROOT import *
from glob import glob
import os
import constants as cnst

gROOT.SetBatch(True)

outdir = 'allplots'
if not os.path.exists(outdir):                                            
    os.makedirs(outdir) 

outfiles = 'Vfb_files'
if not os.path.exists(outfiles):                                            
    os.makedirs(outfiles) 


doses = [0,1,2,5,10,15,20,30,40,70,100,181,200,394,436,509,749,762,1030]


def getFileName(sample,structure,dose,freq=False):
    files = glob('Diode_{}_{}_{}kGy*.root'.format(sample,structure,dose))
    if len(files)==0 and dose == 0:
        files = glob('Diode_{}_{}_pre*.root'.format(sample,structure,dose))
    
    if sample == '3101_LR' and structure == 'MOS2000' and dose == 762: 
        files = glob('Diode_{}_{}_{}kGy.root'.format(sample,structure,dose))

    if freq:
        files = [f for f in files if '1kHz' in f]
    else:
        files = [f for f in files if not '1kHz' in f]

    if len(files)>0: 
        return files[-1]
    else: return

def getPlot(sample,structure,dose,freq=False):
    filename = getFileName(sample,structure,dose,freq)
    if filename == None: return
    tf = TFile.Open(filename,'READ')
    tge = tf.Get('tge_0')
    tf.Close()
    return tge

def graph_derivative(g):
    der = TGraph()
    for i in range(0,g.GetN()-1):
        der.SetPoint(i,(g.GetPointX(i+1)+g.GetPointX(i))/2.,(g.GetPointY(i+1)-g.GetPointY(i))/(g.GetPointX(i+1)-g.GetPointX(i)))
    return der

def cutGraph(old):
    new = TGraphErrors()
    X = list(old.GetX())
    Y = list(old.GetY())
    EX = list(old.GetEX())
    EY = list(old.GetEY())
    i = Y.index(min(Y))
    X = X[i:]
    Y = Y[i:]
    EX = EX[i:]
    EY = EY[i:]

    for i,x in enumerate(X):
        new.SetPoint(i,x,Y[i])
        new.SetPointError(i,EX[i],EY[i])

    return new


def findX(yy,tge):
    X = list(tge.GetX())
    Y = list(tge.GetY())
    for i,y in enumerate(Y):
        if y>yy: break
    return (X[i]+X[i-1])*.5


def fitVfb(sample,structure,dose,freq=False):

    tge = getPlot(sample,structure,dose,freq)
    if tge == None: return

    if sample == '1112_LR' and structure == 'MOShalf':
        tge.RemovePoint(tge.GetN()-1)
        tge.RemovePoint(tge.GetN()-1)
        tge.RemovePoint(tge.GetN()-1)

    cut = True
    if sample == '3009_LR' and structure == 'MOShalf' and dose == 70 and freq == True:
        cut = False

    if cut: 
        tge = cutGraph(tge)
    
    c = TCanvas()

    minC = min(list(tge.GetY()))
    maxC = max(list(tge.GetY()))
    diff = maxC-minC

    if structure =='MOS2000' and maxC<200:
        return

    low_ramp = findX (minC + .5 * diff, tge)
    high_ramp = findX (minC + .9 * diff, tge)

    if sample == '3101_LR' and structure == 'MOS2000' and dose == 762:
        low_ramp = findX (minC + .6 * diff, tge)
        high_ramp = findX (minC + .9 * diff, tge)

    if sample == '1011_LR' and structure == 'MOS2000' and dose == 2:
        low_ramp = findX (minC + .45 * diff, tge)
        high_ramp = findX (minC + .85 * diff, tge)
    if sample == '1008_LR' and structure == 'MOS2000' and (dose == 2 or dose ==1):
        low_ramp = findX (minC + .7 * diff, tge)
        high_ramp = findX (minC + .85 * diff, tge)
    if sample == '1006_LR' and structure == 'MOS2000' and dose == 10:
        low_ramp = findX (minC + .65 * diff, tge)
    if sample == '3101_LR' and structure == 'MOS2000' and dose == 1030:
        low_ramp = findX (minC + .7 * diff, tge)
        high_ramp = findX (minC + .95 * diff, tge)
    if sample == '3010_LR' and structure == 'MOS2000' and dose == 2:
        low_ramp = 135
        high_ramp = 140



    if sample == '3009_LR' and structure == 'MOS2000' and dose == 1 and freq == False:
        high_ramp -= 3
    if sample == '3009_LR' and structure == 'MOShalf' and dose == 70 and freq == True:
        low_ramp = 135
        high_ramp = 155


    if dose == 0:
        low_ramp = findX (minC + .3 * diff, tge)
        high_ramp = findX (minC + .7 * diff, tge)

    if '1008' in sample and dose == 1 and structure == 'MOShalf':
        low_ramp = 31.5
        high_ramp = 33.5


        

    ramp = TF1('ramp','pol1(0)',low_ramp,high_ramp)
    tge.Fit(ramp,'q','',low_ramp,high_ramp)

    low_plat = high_ramp*1.1
    high_plat = high_ramp*1.2

    if dose == 0:
        low_plat = high_ramp*1.5
        high_plat = high_ramp*1.7
        maxV = max(list(tge.GetX()))
        if low_plat > maxV:
            high_plat = maxV
            low_plat = .9*maxV
        if sample == '1008_LR' or sample == '1010_UL' or sample == '3001_UL':
            if structure == 'MOShalf':
                low_plat = .8 * maxV
        if sample == '23_SE_GCD' or sample == 'N0538_25_LR' or sample == '3007_UL':
            low_plat = 5
            high_plat = 7
    if sample == '1006_LR' and structure == 'MOS2000' and dose >=10:
        high_plat = max(list(tge.GetX()))
        low_plat = .95 * high_plat
    if sample == 'N0538_25_LR' and structure == 'MOS2000' and dose ==5:
        high_plat = max(list(tge.GetX()))
        low_plat = .95 * high_plat

    if sample == '3010_LR' and structure == 'MOS2000' and dose == 2:
        low_plat = 145
        high_ramp = 150

    if sample == '24_E_MOS' and structure == 'MOSc2' and dose == 2:
        low_plat = 145
        high_ramp = 150


    if '1009' in sample and dose == 40 and structure == 'MOShalf':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '1011_LR' in sample and dose == 20 and structure == 'MOShalf':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '3001' in sample and dose == 70 and structure == 'MOShalf':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '1112_LR' in sample and dose == 100 and structure == 'MOShalf':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '1011_LR' in sample and dose == 10 and structure == 'MOS2000':
        low_plat = high_ramp*1.03
        high_plat = high_ramp*1.1
    if '1011_LR' in sample and dose == 2 and structure == 'MOS2000':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '1008_LR' in sample and dose == 2 and structure == 'MOS2000':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '1113_LR' in sample and dose == 5 and structure == 'MOS2000':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if '3001_UL' in sample and dose == 10 and structure == 'MOS2000':
        low_plat = high_ramp*1.05
        high_plat = high_ramp*1.1
    if sample == '23_SE_GCD' and dose == 70:
        high_plat = max(list(tge.GetX()))
        low_plat = high_plat *.95
    if sample == 'N0538_25_LR' and dose == 20:
        high_plat = max(list(tge.GetX()))
        low_plat = high_plat *.95
    


    plat = TF1('plat','pol1(0)',low_plat,high_plat)
    tge.Fit(plat,'q','',low_plat,high_plat)

    Vfb = (ramp.GetParameter(0)-plat.GetParameter(0))/(ramp.GetParameter(1)-plat.GetParameter(1))*(-1.)

    tge.Draw('ap')
    plat.Draw('l same')
    ramp.Draw('l same')

    ramp_ext = TF1('ramp_ext','pol1(0)',high_ramp,Vfb+5)
    plat_ext = TF1('plat_ext','pol1(0)',Vfb-10,low_plat)
    ramp_ext.SetParameters(ramp.GetParameter(0),ramp.GetParameter(1))
    plat_ext.SetParameters(plat.GetParameter(0),plat.GetParameter(1))
    ramp_ext.SetLineColor(kBlue)
    plat_ext.SetLineColor(kBlue)

    ramp_ext.Draw('l same')
    plat_ext.Draw('l same')

    l = TLine(Vfb,minC,Vfb,maxC)
    l.SetLineColor(kGreen+1)
    l.Draw('l same')
    
    if freq:
        c.SaveAs('{}/fit_{}_{}_{}kGy_1kHz.png'.format(outdir,sample,structure,dose))
    else:
        c.SaveAs('{}/fit_{}_{}_{}kGy.png'.format(outdir,sample,structure,dose))
    return Vfb


def calculate_parameters(V_fb, structure, C_ox):

    A = cnst.A_MOShalf
    if structure == 'MOS2000':
        A = cnst.A_MOS2000
        if C_ox > 700: A = cnst.A_MOS_6inch
    elif structure == 'MOSc1' or structure == 'MOSc2':
        A = cnst.A_MOS_tracker_circle
    elif structure == 'MOS2s1' or structure == 'MOSs2' or structure == 'MOS':
        A = cnst.A_MOS_tracker_square


    if sample == '1112_LR': #cables inverted
        A = cnst.A_MOS2000
        if structure == 'MOS2000':
            A = cnst.A_MOShalf
        
    A *= 1E-6 # in m^2
    C_ox *= 1E-12 # in F

    phi_s = cnst.Chi + cnst.Eg/2. + cnst.KbTn20*log(cnst.NA/cnst.ni)
    phi_ms = cnst.phi_m - phi_s

    N_ox = C_ox / (A*cnst.q) * (phi_ms + V_fb) # 1/m^2
    N_ox *= 1E-04 # in 1/cm^2

    t_ox = cnst.e0 * cnst.er *A / C_ox
    t_ox *= 1E09 # in nm

    return [N_ox, t_ox]


def processMOS(sample,structure,Cox,freq=False):
    # f = open('{}/{}_{}.txt'.format(outfiles,sample,structure),'w')
    # f.write('dose [kGy] \t V_fb [-V] \t N_ox [1/cm2]\n\n')
    gVfb = TGraph()
    gNox = TGraph()
    gVfb.SetName('gVfb')
    gNox.SetName('gNox')

    for dose in doses:
        if sample == '3009_LR' and structure == 'MOShalf' and dose == 1 and freq == False:
            continue
        if sample == '3101_LR' and dose == 100:
            continue
        if sample == '1011_LR' and dose == 100:
            continue
        if sample == '1006_LR' and structure == 'MOS2000' and dose == 40:
            continue
        if sample == '1113_LR' and structure == 'MOS2000' and dose == 40:
            continue
        if sample == '3103_LR' and structure == 'MOS2000' and dose == 40:
            continue
        if sample == '3001_UL' and structure == 'MOS2000' and dose == 40:
            continue
        if sample == '3007_UL' and structure == 'MOS2000' and dose == 40:
            continue
        if sample == '3101_LR' and structure == 'MOS2000' and dose == 762:
            continue

        Vfb = fitVfb(sample,structure,dose,freq)
        if Vfb == None : continue
        Nox, tox = calculate_parameters(Vfb, structure, Cox)
        # f.write('{} \t {} \t {} \n'.format(dose,Vfb,Nox))
        gVfb.SetPoint(gVfb.GetN(),dose,Vfb)
        gNox.SetPoint(gNox.GetN(),dose,Nox)
    # f.close()

    if freq:
        tf = TFile.Open('{}/dose_{}_{}_1kHz.root'.format(outfiles,sample,structure),'recreate')
    else:
        tf = TFile.Open('{}/dose_{}_{}.root'.format(outfiles,sample,structure),'recreate')
    gVfb.Write()
    gNox.Write()

    c = TCanvas()
    gVfb.SetTitle('{} {}; dose [kGy]; V flat-band [-V]'.format(sample,structure))
    gVfb.SetMarkerStyle(7)
    gVfb.Draw('apl')
    if freq:
        c.SaveAs('{}/dose_{}_{}_Vfb_1kHz.png'.format(outdir,sample,structure))
    else:
        c.SaveAs('{}/dose_{}_{}_Vfb.png'.format(outdir,sample,structure))
    c.Clear()
    gNox.SetTitle('{} {}; dose [kGy]; oxide charge density [1/cm2]'.format(sample,structure))
    gNox.SetMarkerStyle(7)
    gNox.Draw('apl')
    if freq:
        c.SaveAs('{}/dose_{}_{}_Nox_1kHz.png'.format(outdir,sample,structure))
    else:
        c.SaveAs('{}/dose_{}_{}_Nox.png'.format(outdir,sample,structure))

    return

def getCox(sample,structure):
    tge = getPlot(sample,structure,0)
    Cox = max(list(tge.GetY()))
    return Cox

def calculate_GCD_parameters(I,sample):
    I *= 1E-09 # in A
    A = cnst.A_GCD
    if sample == '3009_LR' or sample == '3010_LR':
        A = cnst.A_GCD_6inch
    elif '_SE_' in sample:
        A = cnst.A_GCD_tracker
    A *= 1E-6 # in m^2
    ni = cnst.ni * 1E+06 # in m^-3
    J = I / (cnst.q*ni*A) # in m/s
    J *= 100 # in cm/s
    return J 

def removeBadPoints(tge,threshold):
    eY = list(tge.GetEY())
    Y = list(tge.GetY())
    # relerr = [i/j for  i,j in zip(eY,Y)]
    if max(Y)==min(Y):
        return tge
    relerr = [i/(max(Y)-min(Y)) for  i in eY]

    for i, re in enumerate(relerr):
        if re > threshold:
            tge.RemovePoint(i)
            break
    if i < len(relerr)-1:
        tge = removeBadPoints(tge,threshold)
    return tge

def findApproxDepletion(sample,dose,tge):
    X = list(tge.GetX())
    Y = list(tge.GetY())
    eY = list(tge.GetEY())
    baseline = min(Y)
    Y = [y-baseline for y in Y]
    for i,y in enumerate(Y):
        if y > max(Y)*.3: break
    
    xL = X[i]-10
    xH = X[i]+10

    if sample == '3103_LR' and dose == 40:
        xH += 10
    if sample == '3101_LR':
        xL -= 20
        if dose > 1000:
            xL -= 10
    if sample == '1010_UL' and dose == 1:
        xL += 5
    if sample == '3009_LR' and dose >= 20:
        xL -= 15
        xH += 20
    if sample == '1006_LR' and dose >= 70:
        xL -= 20

    if sample == '3010_LR' and dose >= 40:
        xL -= 20
        xH += 20

    if sample == '3010_LR' and dose == 20:
        xH +=10
        
    if sample == '23_SE_GCD' and dose >=40:
        xH +=30
        xL -=20
    if sample == 'N0538_25_LR' and dose == 1:
        xH -= 7
        xL -= 10
    if sample == 'N0538_25_LR' and dose >= 40:
        xL -= 20
        xH += 20
    if sample == '3007_UL' and dose >= 20:
        xL -= 20

    ym = +999
    yM = -999
    xm = -999
    xM = +999
    eM = 0
    em = 0

    for i,x in enumerate(X):
        if x < xL or x > xH:
            continue
        if Y[i] > yM: 
            yM = Y[i]
            eM = eY[i]
            xM = x
        if Y[i] < ym: 
            ym = Y[i]
            em = eY[i]
            xm = x
    return [xm,ym+baseline,xM,yM+baseline,(em**2+eM**2)**.5]

def cutGCDcurve(tge,cut):
    if list(tge.GetX())[-1] > cut:
        tge.RemovePoint(tge.GetN()-1)
    if list(tge.GetX())[-1] > cut:
        tge = cutGCDcurve(tge,cut)

    tge.SetMaximum(max(list(tge.GetY()))*1.1)
    return tge

def cutGCDcurveLow(tge,cut):
    if list(tge.GetX())[0] < cut:
        tge.RemovePoint(0)
    if list(tge.GetX())[0] < cut:
        tge = cutGCDcurveLow(tge,cut)

    tge.SetMaximum(max(list(tge.GetY()))*1.1)
    return tge

def getGCDcurrent(sample,dose):
    tge = getPlot(sample,'GCD',dose)
    if tge == None: return

    if sample == '1112_LR':
        tge = cutGCDcurve(tge,50)
    if sample == '3103_LR' and dose == 20:
        tge = cutGCDcurve(tge,40)
    if sample == '3103_LR' and dose == 40:
        tge = cutGCDcurve(tge,47)
    if sample == '3003_UL' and dose == 5:
        tge.RemovePoint(tge.GetN()-1)
        tge = cutGCDcurve(tge,40)
    if sample == '1012_UL' and dose == 1:
        tge.RemovePoint(tge.GetN()-1)
        tge.SetMinimum(0)
        tge.SetMaximum(.4)
    if sample == '1011_LR' and dose <= 5:
        tge = cutGCDcurve(tge,40)
    if sample == '1011_LR' and dose >= 10:
        tge = cutGCDcurve(tge,55)
    if sample == '1109_LR' and dose == 40:
        tge = cutGCDcurveLow(tge,50)
    if sample == '1109_LR' and dose == 1:
        tge = cutGCDcurveLow(tge,-2)
    if sample == '1109_LR' and dose >= 40:
        tge = cutGCDcurve(tge,80)
    if sample == '3007_UL' and dose == 20:
        tge = cutGCDcurve(tge,45)
    if sample == '3007_UL' and dose == 40:
        tge = cutGCDcurve(tge,50)



    tge_orig = tge.Clone()    
    threshold = 0.05
    if sample == '3009_LR' and dose == 2:
        threshold = 0.1
    if sample == '1006_LR' and dose == 1:
        threshold = 0.1
    tge = removeBadPoints(tge,threshold)

    xm, ym, xM, yM, e = findApproxDepletion(sample,dose,tge)

    at = TGraph()
    at.SetPoint(0,xm,ym)
    at.SetPoint(1,xM,yM)
    at.SetMarkerStyle(8)
    at.SetMarkerColor(kGreen)
        
    c = TCanvas()
    tge_orig.SetLineColor(kRed)
    tge_orig.SetMarkerColor(kRed)
    tge_orig.Draw('apl')
    tge.Draw('pl same')
    at.Draw('p same')
    c.SaveAs('{}/fit_{}_GCD_{}kGy.png'.format(outdir,sample,dose))

    return [yM-ym,e]

def processGCD(sample):

    if sample == '1008_LR': return
    if sample == '1113_LR': return
    # if sample == '1112_LR': return
    if sample == '1105_LR': return

    gI = TGraphErrors()
    gJ = TGraphErrors()
    gI.SetName('gI')
    gJ.SetName('gJ')

    for dose in doses:
        if dose==0: continue
        if sample == '3103_LR' and dose >=70: continue
        if sample == '3101_LR' and dose ==100: continue
        if sample == '1112_LR' and dose !=1 : continue
        if sample == '23_SE_GCD' and dose <=1: continue
        if sample == '3007_UL' and dose >=70: continue

        Ie = getGCDcurrent(sample,dose)
        if Ie == None : continue
        I = Ie[0]
        e = Ie[1]
        J = calculate_GCD_parameters(I,sample)
        gI.SetPoint(gI.GetN(),dose,I)
        gJ.SetPoint(gJ.GetN(),dose,J)
        gI.SetPointError(gI.GetN()-1,0,e)
        gJ.SetPointError(gJ.GetN()-1,0,e*J/I)


    tf = TFile.Open('{}/dose_{}_GCD.root'.format(outfiles,sample),'recreate')
    gI.Write()
    gJ.Write()

    c = TCanvas()
    gI.SetTitle('{} GCD; dose [kGy]; GCD current [nA]'.format(sample))
    gI.SetMarkerStyle(7)
    gI.Draw('apl')
    c.SaveAs('{}/dose_{}_GCD_I.png'.format(outdir,sample))
    c.Clear()
    gJ.SetTitle('{} GCD; dose [kGy]; surface velocity [cm/s]'.format(sample))
    gJ.SetMarkerStyle(7)
    gJ.Draw('apl')
    c.SaveAs('{}/dose_{}_GCD_J.png'.format(outdir,sample))

    return

def processSample(sample):
    structures = ['MOShalf','MOS2000']
    if '_E_' in sample:
        structures = ['MOSc1','MOSc2','MOSs2']
    elif '_SE_' in sample:
        structures = ['MOS']

    for structure in structures:
        if sample == '1012_UL': break

        Cox = getCox(sample,structure)
        processMOS(sample,structure,Cox-cnst.approx_openC)
        if sample == '3009_LR':
            processMOS(sample,structure,Cox-cnst.approx_openC,freq=True)
    if not '_E_' in sample:
            processGCD(sample)
    return


# samples = ['1006_LR','1008_LR','1009_LR','1010_UL','1011_LR','1003_LR','1113_LR','3009_LR',
#            '3001_UL','1112_LR','3003_UL','3103_LR','1109_LR','1105_LR','3101_LR']

# samples = ['3010_LR','24_E_MOS','23_SE_GCD','N0538_25_LR']
# samples = ['3007_UL','1012_UL']

# for sample in samples:
#     processSample(sample)


