# region modules
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import AnchoredText
from scipy import stats
from scipy.optimize import minimize
from pyswarm import pso
# from . import HBV as hbv
import HBV as hbv
# from . import objectivefunctions as obj
import objectivefunctions as obj

#
# import HBV as hbv
# import objectivefunctions as obj

# endregion


seaborn.set()
np.seterr(all='ignore')


class Hbv(object):
    _dir = r'D:\DRIVE\TUBITAK\Hydro_Model\Data\Darbogaz'
    _data = "Darbogaz.csv"

    def __init__(self, area, input_parameters, States, calibration=False, method='PSO', Objective_fun='nse',
                 maxiter=15, Spinoff=0):
        self._working_directory = None
        self.Data_file = None
        self.df = None
        self.P = None
        self.T = None
        self.E = None
        self.Qobs = None
        self.p2 = [24, area]
        self.area = area / (3.6 * 24)
        self.Area = area
        self.Spinoff = Spinoff
        self.parameters = None
        self.Qfit = None
        self.dfh = None
        # self.initial = np.array([10, 100, 0.5, 500, 10, 0.5, 0.5, 0, 2000, 2.15,2])
        # self.initial = np.array([5.59441567e+00,6.85168038e+02,1.30412167e-01,8.47239393e+02,4.00934557e+01,4.21557738e-01,4.88201564e-01,4.09627612e-02,1.67517734e+03,4.09537018e-01,3.71693424e+00])
        self.initial = np.array(input_parameters)
        self.Qsim = None
        self.n = None
        self.Date = None
        self.lb = [-1.5, 0.001, 0.001, 0.04, 50.0, 0.6, 0.001, 0.2, 0.00042, 0.0000042, 0.001, 1.0, 0.001, 0.01, 0.0,
                   0.001,
                   0.6, 0.4, 1]
        self.ub = [2.5, 3.0, 2.0, 0.4, 500.0, 1.4, 5.0, 0.5, 0.0167, 0.00062, 1.0, 6.0, 0.1, 1.0, 0.08, 0.125, 1.4, 1.4,
                   10]
        self.bounds = list(zip(self.lb, self.ub))
        self.NSE = None
        self.RMSE = None
        self.PBIAS = None
        self.Cal = calibration
        self.statistics = None
        self.export = 'Result.csv'
        self.flowduration = None
        self.method = method
        self.St = None
        self.Objective_fun = Objective_fun
        self.maxiter = maxiter
        self.States = States

    @property
    def process_path(self):
        return self._working_directory

    @process_path.setter
    def process_path(self, value):
        self._working_directory = value
        pass

    def DataRead(self):
        self.df = pd.read_csv(self.Data_file, sep=',',
                              parse_dates=[0], header=0)
        self.df = self.df.set_index('Date')

    def InitData(self):
        self.P = self.df.P
        self.T = self.df.Temp
        self.E = self.df.E
        self.Qobs = self.df.Q
        self.n = self.df.__len__()
        self.Qsim = np.zeros(self.n)
        self.Date = self.df.index.to_pydatetime()

    def Objective(self, x, *args):
        # self.Qsim, self.St = nam_f.nam_method(
        #     x,self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=True)
        self.Qsim, self.St = hbv.simulate(self.P, self.T, self.E, x, self.p2)
        # n = math.sqrt((sum((self.Qsim - self.Qobs) ** 2)) / len(self.Qobs))
        # n = self.nash(self.Qobs, self.Qsim)
        # mean_observed = np.nanmean(self.Qobs)
        # numerator = np.nansum((self.Qobs - self.Qsim) ** 2)
        # denominator = np.nansum((self.Qobs - mean_observed) ** 2)
        # n = 1 - (numerator / denominator)
        # Q = np.where(self.Qobs > 10, np.nan, self.Qobs)
        Qobs = self.Qobs[self.Spinoff:]
        Qsim = self.Qsim[self.Spinoff:]
        if self.Objective_fun == 'nse':
            n = 1 - obj.nashsutcliffe(Qobs, Qsim)
        elif self.Objective_fun == 'kge':
            n = 1 - obj.kge(Qobs, Qsim)
        elif self.Objective_fun == 'volume':
            n = obj.volume_error(Qobs, Qsim)
        elif self.Objective_fun == 'rmse':
            n = obj.rmse(Qobs, Qsim)
        elif self.Objective_fun == 'r2':
            n = 1 - obj.rsquared(Qobs, Qsim)
        elif self.Objective_fun == 'rmpw':
            n = obj.peak_(Qobs, Qsim)
        elif self.Objective_fun == 'nslf':
            n = obj.low_(Qobs, Qsim)
        else:
            n = obj.rmse(Qobs, Qsim)
        # n = obj.nashsutcliffe(Q, self.Qsim)
        return n

    def run(self):
        self.DataRead()
        self.InitData()
        if self.Cal:
            if self.method == 'PSO':
                args = (self.P, self.T, self.E, self.area, self.Spinoff, self.Qobs)
                xopt, fopt, = pso(self.Objective, self.lb, self.ub, f_ieqcons=None, args=args, maxiter=self.maxiter,
                                  debug=True)
                # self.Qsim, self.St = nam_f.nam_method(
                #     xopt,self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=False)
                self.Qsim, self.St = hbv.simulate(self.P, self.T, self.E, xopt, self.p2)
                self.parameters = xopt
            else:
                self.parameters = minimize(self.Objective, self.initial, method='SLSQP', bounds=self.bounds,
                                           options={'maxiter': 1e8, 'disp': False})
                self.Qsim, self.St = hbv.simulate(self.P, self.T, self.E, self.parameters.x, self.p2)
                # self.Qsim, self.St = nam_f.nam_method(
                #     self.parameters.x, self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=False)
                self.parameters = self.parameters.x
        else:
            self.Qsim, self.St = hbv.simulate(self.P, self.T, self.E, self.initial, self.p2)
            # self.Qsim, self.St = nam_f.nam_method(
            #     self.initial, self.States, self.P, self.T, self.E, self.area, self.Spinoff)
            self.parameters = self.initial

    def update(self):
        fit = self.interpolation()
        self.Qfit = fit(self.Qobs)
        self.df['Qsim'] = self.Qsim
        self.df['Qfit'] = self.Qfit
        self.flowduration = pd.DataFrame()
        self.flowduration['Qsim_x'] = self.flowdur(self.Qsim)[0]
        self.flowduration['Qsim_y'] = self.flowdur(self.Qsim)[1]
        self.flowduration['Qobs_x'] = self.flowdur(self.Qobs)[0]
        self.flowduration['Qobs_y'] = self.flowdur(self.Qobs)[1]
        # self.df.to_csv(os.path.join(self.process_path, self.export), index=True, header=True)

    def stats(self):
        mean = np.nanmean(self.Qobs[self.Spinoff:])
        # mean2 = np.mean(self.Qsim)
        self.NSE = 1 - (np.nansum((self.Qsim[self.Spinoff:] - self.Qobs[self.Spinoff:]) ** 2) /
                        np.nansum((self.Qobs[self.Spinoff:] - mean) ** 2))
        self.RMSE = np.sqrt(
            np.nansum((self.Qsim[self.Spinoff:] - self.Qobs[self.Spinoff:]) ** 2) / len(self.Qsim[self.Spinoff:]))
        self.PBIAS = (np.nansum(self.Qobs[self.Spinoff:] - self.Qsim[self.Spinoff:]) / np.nansum(
            self.Qobs[self.Spinoff:])) * 100
        self.statistics = obj.calculate_all_functions(self.Qobs[self.Spinoff:], self.Qsim[self.Spinoff:])

    def interpolation(self):
        idx = np.isfinite(self.Qobs[self.Spinoff:]) & np.isfinite(self.Qsim[self.Spinoff:])
        fit = np.polyfit(self.Qobs[self.Spinoff:][idx], self.Qsim[self.Spinoff:][idx], 1)
        fit_fn = np.poly1d(fit)
        return fit_fn

    def draw(self):
        self.stats()
        fit = self.interpolation()
        self.Qfit = fit(self.Qobs[self.Spinoff:])
        width = 15  # Figure width
        height = 10  # Figure height
        f = plt.figure(figsize=(width, height))
        widths = [2, 2, 2]
        heights = [2, 3, 1]
        gs = GridSpec(3, 3, figure=f, width_ratios=widths,
                      height_ratios=heights)
        ax1 = f.add_subplot(gs[1, :])
        ax2 = f.add_subplot(gs[0, :], sharex=ax1)
        ax3 = f.add_subplot(gs[-1, 0])
        ax4 = f.add_subplot(gs[-1, -1])
        ax5 = f.add_subplot(gs[-1, -2])
        color = 'tab:blue'
        ax2.set_ylabel('Precipitation ,mm ', color=color,
                       style='italic', fontweight='bold', labelpad=20, fontsize=13)
        ax2.bar(self.Date[self.Spinoff:], self.df.P[self.Spinoff:], color=color,
                align='center', alpha=0.6, width=1)
        ax2.tick_params(axis='y', labelcolor=color)
        # ax2.set_ylim(0, max(self.df.P) * 1.1, )
        ax2.set_ylim(max(self.df.P[self.Spinoff:]) * 1.1, 0)
        ax2.legend(['Precipitation'])
        color = 'tab:red'
        ax2.set_title('NAM Simulation', style='italic',
                      fontweight='bold', fontsize=16)
        ax1.set_ylabel(r'Discharge m$^3$/s', color=color,
                       style='italic', fontweight='bold', labelpad=20, fontsize=13)
        ax1.plot(self.Date[self.Spinoff:], self.Qobs[self.Spinoff:], 'b-', self.Date[self.Spinoff:],
                 self.Qsim[self.Spinoff:], 'r--', linewidth=2.0)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.tick_params(axis='x', labelrotation=45)
        ax1.set_xlabel('Date', style='italic',
                       fontweight='bold', labelpad=20, fontsize=13)
        ax1.legend(('Observed Run-off', 'Simulated Run-off'), loc=2)
        plt.setp(ax2.get_xticklabels(), visible=False)
        anchored_text = AnchoredText("NSE = %.2f\nRMSE = %0.2f\nPBIAS = %0.2f" % (self.NSE, self.RMSE, self.PBIAS),
                                     loc=1, prop=dict(size=11))
        ax1.add_artist(anchored_text)
        # plt.subplots_adjust(hspace=0.05)
        ax3.set_title('Flow Duration Curve', fontsize=11, style='italic')
        ax3.set_yscale("log")
        ax3.set_ylabel(r'Discharge m$^3$/s', style='italic',
                       fontweight='bold', labelpad=20, fontsize=9)
        ax3.set_xlabel('Percentage Exceedence (%)', style='italic',
                       fontweight='bold', labelpad=20, fontsize=9)
        exceedence, sort, low_percentile, high_percentile = self.flowdur(
            self.Qsim[self.Spinoff:])
        ax3.legend(['Precipitation'])
        ax3.plot(self.flowdur(self.Qsim[self.Spinoff:])[0], self.flowdur(self.Qsim[self.Spinoff:])[1], 'b-',
                 self.flowdur(self.Qobs[self.Spinoff:])[0],
                 self.flowdur(self.Qobs[self.Spinoff:])[1], 'r--')
        # ax3.plot(self.flowdur(self.Qobs)[0], self.flowdur(self.Qobs)[1])
        ax3.legend(('Observed', 'Simulated'),
                   loc="upper right", prop=dict(size=7))

        plt.grid(True, which="minor", ls="-")

        st = stats.linregress(self.Qobs[self.Spinoff:], self.Qsim[self.Spinoff:])
        # ax4.set_yscale("log")
        # ax4.set_xscale("log")
        ax4.set_title('Regression Analysis', fontsize=11, style='italic')
        ax4.set_ylabel(r'Simulated', style='italic',
                       fontweight='bold', labelpad=20, fontsize=9)
        ax4.set_xlabel('Observed', style='italic',
                       fontweight='bold', labelpad=20, fontsize=9)
        anchored_text = AnchoredText("y = %.2f\n$R^2$ = %0.2f" % (
            st[0], (st[2]) ** 2), loc=4, prop=dict(size=7))
        # ax4.plot(self.Qobs, fit(self.Qsim), '--k')
        # ax4.scatter(self.Qsim, self.Qobs)
        ax4.plot(self.Qobs[self.Spinoff:], self.Qsim[self.Spinoff:], 'bo', self.Qobs[self.Spinoff:], self.Qfit, '--k')
        ax4.add_artist(anchored_text)

        self.update()
        self.dfh = self.df.resample('M').mean()
        Date = self.dfh.index.to_pydatetime()
        ax5.set_title('Monthly Mean', fontsize=11, style='italic')
        ax5.set_ylabel(r'Discharge m$^3$/s', color=color,
                       style='italic', fontweight='bold', labelpad=20, fontsize=9)
        # ax5.set_xlabel('Date', style='italic', fontweight='bold', labelpad=20, fontsize=9)
        ax5.tick_params(axis='y', labelcolor=color)
        ax5.tick_params(axis='x', labelrotation=45)
        # ax5.set_xlabel('Date', style='italic', fontweight='bold', labelpad=20, fontsize=9)
        ax5.legend(('Observed', 'Simulated'), loc="upper right")
        exceedence, sort, low_percentile, high_percentile = self.flowdur(
            self.Qsim[self.Spinoff:])
        ax5.tick_params(axis='x', labelsize=9)
        ax5.plot(Date, self.dfh.Q, 'b-', Date,
                 self.dfh.Qsim, 'r--', linewidth=2.0)
        ax5.legend(('Observed', 'Simulated'), prop={'size': 7}, loc=1)
        # ax5.plot(dfh.Q)
        # ax5.plot(dfh.Qsim)
        # ax5.legend()
        plt.grid(True, which="minor", ls="-")
        plt.subplots_adjust(hspace=0.03)
        # self.St.plot(subplots=True, layout=(4, 2), figsize=(12, 8))
        f.tight_layout()
        plt.show()

    def flowdur(self, x):
        exceedence = np.arange(1., len(np.array(x)) + 1) / len(np.array(x))
        exceedence *= 100
        sort = np.sort(x, axis=0)[::-1]
        low_percentile = np.percentile(sort, 5, axis=0)
        high_percentile = np.percentile(sort, 95, axis=0)
        return exceedence, sort, low_percentile, high_percentile

    def drawflow(self):
        f = plt.figure(figsize=(15, 10))
        ax = f.add_subplot(111)
        # fig, ax = plt.subplots(1, 1)
        ax.set_yscale("log")
        ax.set_ylabel(r'Discharge m$^3$/s', style='italic',
                      fontweight='bold', labelpad=20, fontsize=13)
        ax.set_xlabel('Percentage Exceedence (%)', style='italic',
                      fontweight='bold', labelpad=20, fontsize=13)
        exceedence, sort, low_percentile, high_percentile = self.flowdur(
            self.Qsim)
        ax.plot(self.flowdur(self.Qsim)[0], self.flowdur(self.Qsim)[1])
        ax.plot(self.flowdur(self.Qobs)[0], self.flowdur(self.Qobs)[1])
        plt.grid(True, which="minor", ls="-")
        # ax.fill_between(exceedence, low_percentile, high_percentile)
        # plt.show()
        return ax


# Sample Run
if __name__ == '__main__':
    params = [1.06653896e+00, 7.85803777e-01, 1.12456396e+00, 4.00000005e-02
        , 6.52779758e+01, 1.40000000e+00, 2.04563613e-01, 5.00000000e-01
        , 7.23806920e-03, 6.20000000e-04, 5.98308241e-01, 2.29012429e+00
        , 2.32816764e-02, 4.01249854e-01, 0.00000000e+00, 1.25000000e-01
        , 1.19040117e+00, 1.40000000e+00, 6.15462361e+00]
    States = np.array([0, 0, 0.9 * params[1], 0, 0, 0, 0, 0.1])
    n = Hbv(421, params, States, calibration=True, method='PSO', Objective_fun='nse', maxiter=20)
    n.process_path = '/media/D/Datasets'
    n.Data_file = os.path.join(n.process_path, "Cakit_model.csv")
    n.run()
    n.draw()
