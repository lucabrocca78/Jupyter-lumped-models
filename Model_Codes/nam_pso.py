# region modules
import os
import matplotlib.pyplot as plt
import nam_fun as nam_f
import numpy as np
import objectivefunctions as obj
import pandas as pd
import seaborn
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import AnchoredText
from scipy import stats
from scipy.optimize import minimize
from pyswarm import pso

# endregion


seaborn.set()
np.seterr(all='ignore')


class Nam(object):
    _dir = r'D:\DRIVE\TUBITAK\Hydro_Model\Data\Darbogaz'
    _data = "Darbogaz.csv"

    def __init__(self, area, input_parameters, States, calibration=False, method='PSO', Objective_fun='nashsutcliffe',
                 maxiter=15):
        self._working_directory = None
        self.Data_file = None
        self.df = None
        self.P = None
        self.T = None
        self.E = None
        self.Qobs = None
        self.area = area / (3.6 * 24)
        self.Area = area
        self.Spinoff = 0
        self.parameters = None
        self.Qfit = None
        self.dfh = None
        # self.initial = np.array([10, 100, 0.5, 500, 10, 0.5, 0.5, 0, 2000, 2.15,2])
        # self.initial = np.array([5.59441567e+00,6.85168038e+02,1.30412167e-01,8.47239393e+02,4.00934557e+01,4.21557738e-01,4.88201564e-01,4.09627612e-02,1.67517734e+03,4.09537018e-01,3.71693424e+00])
        self.initial = np.array(input_parameters)
        self.Qsim = None
        self.n = None
        self.Date = None
        self.bounds = (
            (0.01, 50), (0.01, 1000), (0.01, 1), (200, 1000), (10,
                                                               50), (0.01, 0.99), (0.01, 0.99), (0.01, 0.99),
            (500, 5000), (0, 4), (-2, 4))
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

    def nash(self, qobserved, qsimulated):
        s, e = np.array(qobserved), np.array(qsimulated)
        # s,e=simulation,evaluation
        mean_observed = np.nanmean(e)
        # compute numerator and denominator
        numerator = np.nansum((e - s) ** 2)
        denominator = np.nansum((e - mean_observed) ** 2)
        # compute coefficient
        return 1 - (numerator / denominator)

    def Objective(self, x, *args):
        self.Qsim, self.St = nam_f.nam_method(
            x, self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=True)
        # n = math.sqrt((sum((self.Qsim - self.Qobs) ** 2)) / len(self.Qobs))
        # n = self.nash(self.Qobs, self.Qsim)
        # mean_observed = np.nanmean(self.Qobs)
        # numerator = np.nansum((self.Qobs - self.Qsim) ** 2)
        # denominator = np.nansum((self.Qobs - mean_observed) ** 2)
        # n = 1 - (numerator / denominator)
        # Q = np.where(self.Qobs > 10, np.nan, self.Qobs)
        wu = 15
        if self.Objective_fun == 'nse':
            n = 1 - obj.nashsutcliffe(self.Qobs[wu:], self.Qsim[wu:])
        elif self.Objective_fun == 'kge':
            n = 1 - obj.kge(self.Qobs, self.Qsim)
        elif self.Objective_fun == 'volume':
            n = obj.volume_error(self.Qobs, self.Qsim)
        elif self.Objective_fun == 'rmse':
            n = obj.rmse(self.Qobs, self.Qsim)
        elif self.Objective_fun == 'r2':
            n = 1 - obj.rsquared(self.Qobs, self.Qsim)
        elif self.Objective_fun == 'rmpw':
            n = obj.peak_(self.Qobs, self.Qsim)
        elif self.Objective_fun == 'nslf':
            n = obj.low_(self.Qobs, self.Qsim)
        else:
            n = obj.rmse(self.Qobs, self.Qsim)
        # n = obj.nashsutcliffe(Q, self.Qsim)
        return n

    def run(self):
        self.DataRead()
        self.InitData()
        if self.Cal:
            if self.method == 'PSO':
                lb = [0.01, 0.01, 0.01, 200, 10, 0.01, 0.01, 0.01, 500, 0, -2]
                ub = [50, 1000, 1, 1000, 50, 0.99, 0.99, 0.99, 5000, 4, 4]
                args = (self.P, self.T, self.E, self.area, self.Spinoff, self.Qobs)
                xopt, fopt = pso(self.Objective, lb, ub, f_ieqcons=None, args=args, maxiter=self.maxiter, debug=True)
                self.Qsim, self.St = nam_f.nam_method(
                    xopt, self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=False)
                self.parameters = xopt
            else:
                self.parameters = minimize(self.Objective, self.initial, method='SLSQP', bounds=self.bounds,
                                           options={'maxiter': 1e8, 'disp': False})
                self.Qsim, self.St = nam_f.nam_method(
                    self.parameters.x, self.States, self.P, self.T, self.E, self.area, self.Spinoff, Cal=False)
                self.parameters = self.parameters.x
        else:
            self.Qsim, self.St = nam_f.nam_method(
                self.initial, self.States, self.P, self.T, self.E, self.area, self.Spinoff)
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
        mean = np.mean(self.Qobs)
        # mean2 = np.mean(self.Qsim)
        self.NSE = 1 - (np.nansum((self.Qsim - self.Qobs) ** 2) /
                        np.nansum((self.Qobs - mean) ** 2))
        self.RMSE = np.sqrt(np.nansum((self.Qsim - self.Qobs) ** 2) / len(self.Qsim))
        self.PBIAS = (np.nansum(self.Qobs - self.Qsim) / np.nansum(self.Qobs)) * 100
        self.statistics = obj.calculate_all_functions(self.Qobs, self.Qsim)

    def interpolation(self):
        idx = np.isfinite(self.Qobs) & np.isfinite(self.Qsim)
        fit = np.polyfit(self.Qobs[idx], self.Qsim[idx], 1)
        fit_fn = np.poly1d(fit)
        return fit_fn

    def draw(self):
        self.stats()
        fit = self.interpolation()
        self.Qfit = fit(self.Qobs)
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
        ax2.bar(self.Date, self.df.P, color=color,
                align='center', alpha=0.6, width=1)
        ax2.tick_params(axis='y', labelcolor=color)
        # ax2.set_ylim(0, max(self.df.P) * 1.1, )
        ax2.set_ylim(max(self.df.P) * 1.1, 0)
        ax2.legend(['Precipitation'])
        color = 'tab:red'
        ax2.set_title('NAM Simulation', style='italic',
                      fontweight='bold', fontsize=16)
        ax1.set_ylabel(r'Discharge m$^3$/s', color=color,
                       style='italic', fontweight='bold', labelpad=20, fontsize=13)
        ax1.plot(self.Date, self.Qobs, 'b-', self.Date,
                 self.Qsim, 'r--', linewidth=2.0)
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
            self.Qsim)
        ax3.legend(['Precipitation'])
        ax3.plot(self.flowdur(self.Qsim)[0], self.flowdur(self.Qsim)[1], 'b-', self.flowdur(self.Qobs)[0],
                 self.flowdur(self.Qobs)[1], 'r--')
        # ax3.plot(self.flowdur(self.Qobs)[0], self.flowdur(self.Qobs)[1])
        ax3.legend(('Observed', 'Simulated'),
                   loc="upper right", prop=dict(size=7))

        plt.grid(True, which="minor", ls="-")

        st = stats.linregress(self.Qobs, self.Qsim)
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
        ax4.plot(self.Qobs, self.Qsim, 'bo', self.Qobs, self.Qfit, '--k')
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
            self.Qsim)
        ax5.tick_params(axis='x', labelsize=9)
        ax5.plot(Date, self.dfh.Q, 'b-', Date,
                 self.dfh.Qsim, 'r--', linewidth=2.0)
        ax5.legend(('Observed', 'Simulated'), prop={'size': 7}, loc=1)
        # ax5.plot(dfh.Q)
        # ax5.plot(dfh.Qsim)
        # ax5.legend()
        plt.grid(True, which="minor", ls="-")
        plt.subplots_adjust(hspace=0.03)
        self.St.plot(subplots=True, layout=(4, 2), figsize=(12, 8))
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
    params = [6.96780205e+00, 4.86098809e+02, 6.66247792e-01, 5.42601108e+02
        , 2.43815545e+01, 8.21285865e-01, 1.00000000e-02, 1.00000000e-02
        , 7.37979357e+02, 9.64180895e-01, 2.06295770e+00]
    States = np.array([0, 0, 0.9 * params[1], 0, 0, 0, 0, 0.1])
    n = Nam(421, params, States, calibration=True, method='PSO', Objective_fun='nse', maxiter=20)
    n.process_path = '/media/D/Datasets'
    n.Data_file = os.path.join(n.process_path, "Cakit_model.csv")
    n.run()
    n.draw()
