import os
from copy import copy

import matplotlib.pyplot as plt
import numpy as np
# To play with any scenario scripts as tutorials, you should make a copy of them into a custom folder
# outside of the Basilisk directory.
#
# To copy them, first find the location of the Basilisk installation.
# After installing, you can find the installed location of Basilisk by opening a python interpreter and
# running the commands:
from Basilisk import __path__

bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])

# import message declarations
from Basilisk.architecture import messaging
from Basilisk.simulation import coarseSunSensor

# import simulation related support
from Basilisk.simulation import spacecraft
# general support file with common unit test functions
# import general simulation support files
from Basilisk.utilities import (SimulationBaseClass, macros, orbitalMotion,
                                simIncludeGravBody, unitTestSupport, vizSupport)
from Basilisk.simulation import magneticFieldCenteredDipole
from Basilisk.utilities import simSetPlanetEnvironment
from Basilisk.simulation import simSynch

def run(show_plots, liveStream, timeStep, orbitCase, useSphericalHarmonics, planetCase, useCSSConstellation, usePlatform, useEclipse, useKelly):
    """
    At the end of the python script you can specify the following example parameters.

    Args:
        show_plots (bool): Determines if the script should display plots
        orbitCase (str):

            ======  ============================
            String  Definition
            ======  ============================
            'LEO'   Low Earth Orbit
            'GEO'   Geosynchronous Orbit
            'GTO'   Geostationary Transfer Orbit
            ======  ============================

        useSphericalHarmonics (Bool): False to use first order gravity approximation: :math:`\\frac{GMm}{r^2}`

        planetCase (str): {'Earth', 'Mars'}
    """
    
    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"

    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()

    #
    #  create the simulation process
    #
    dynProcess = scSim.CreateNewProcess(simProcessName)
    
    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(timeStep)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    #
    #   setup the simulation tasks/objects
    #

    # initialize spacecraft object and set properties
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "bskSat"

    # add spacecraft object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject)

    # setup Gravity Body
    gravFactory = simIncludeGravBody.gravBodyFactory()

    planet = gravFactory.createEarth()
    planet.isCentralBody = True          # ensure this is the central gravitational body
    if useSphericalHarmonics:
        planet.useSphericalHarmParams = True
        simIncludeGravBody.loadGravFromFile(bskPath + '/supportData/LocalGravData/GGM03S-J2-only.txt',
                                            planet.spherHarm, 2)
    mu = planet.mu
    
    # attach gravity model to spacecraft
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))

    #
    #   setup orbit and simulation time
    #
    # setup the orbit using classical orbit elements
    oe = orbitalMotion.ClassicElements()
    rLEO = 7000. * 1000      # meters
    rGEO = 42000. * 1000     # meters
    if orbitCase == 'GEO':
        oe.a = rGEO
        oe.e = 0.00001
        oe.i = 0.0 * macros.D2R
    elif orbitCase == 'GTO':
        oe.a = (rLEO + rGEO) / 2.0
        oe.e = 1.0 - rLEO / oe.a
        oe.i = 0.0 * macros.D2R
    else:                   # LEO case, default case 0
        oe.a = rLEO
        oe.e = 0.0001
        oe.i = 33.3 * macros.D2R
    oe.Omega = 48.2 * macros.D2R
    oe.omega = 347.8 * macros.D2R
    oe.f = 85.3 * macros.D2R
    rN, vN = orbitalMotion.elem2rv(mu, oe)
    oe = orbitalMotion.rv2elem(mu, rN, vN)      # this stores consistent initial orbit elements
    # with circular or equatorial orbit, some angles are arbitrary
    
    # To set the spacecraft initial conditions, the following initial position and velocity variables are set:
    scObject.hub.r_CN_NInit = rN  # m   - r_BN_N
    scObject.hub.v_CN_NInit = vN  # m/s - v_BN_N
    scObject.hub.sigma_BNInit = [[0.0], [0.0], [0.0]]               # sigma_BN_B
    scObject.hub.omega_BN_BInit = [[0.0], [0.0], [1.*macros.D2R]]   # rad/s - omega_BN_B
    
        # Add CSS Sensors
    #
    # create simulation messages
    #
    sunPositionMsgData = messaging.SpicePlanetStateMsgPayload()
    sunPositionMsgData.PositionVector = [orbitalMotion.AU, 0.0, 0.0]
    sunPositionMsg = messaging.SpicePlanetStateMsg().write(sunPositionMsgData)

    if useEclipse:
        eclipseMsgData = messaging.EclipseMsgPayload()
        eclipseMsgData.shadowFactor = 1
        eclipseMsg = messaging.EclipseMsg().write(eclipseMsgData)

    def setupCSS(CSS):
        CSS.fov = 180. * macros.D2R
        CSS.scaleFactor = 0.0001
        CSS.maxOutput = 100.0
        CSS.minOutput = 0.0
        CSS.CSSGroupID = 0
        CSS.r_B = [2.00131, 2.36638, 1.]
        CSS.sunInMsg.subscribeTo(sunPositionMsg)
        CSS.stateInMsg.subscribeTo(scObject.scStateOutMsg)
        if useKelly:
            CSS.kellyFactor = 0.2
        if useEclipse:
            CSS.sunEclipseInMsg.subscribeTo(eclipseMsg)
        if usePlatform:
            CSS.setBodyToPlatformDCM(90. * macros.D2R, 0., 0.)
            CSS.theta = -90. * macros.D2R
            CSS.phi = 0 * macros.D2R
            CSS.setUnitDirectionVectorWithPerturbation(0., 0.)
        else:
            CSS.nHat_B = np.array([1.0, 0.0, 0.0])

    # In both CSS simulation scenarios (A) and (B) the CSS modules must
    # first be individually created and configured.
    # In this simulation each case uses two CSS sensors.  The minimum
    # variables that must be set for each CSS includes
    CSS1 = coarseSunSensor.CoarseSunSensor()
    CSS1.ModelTag = "CSS1_sensor"
    setupCSS(CSS1)

    CSS2 = coarseSunSensor.CoarseSunSensor()
    CSS2.ModelTag = "CSS2_sensor"
    setupCSS(CSS2)
    CSS2.CSSGroupID = 0
    CSS2.r_B = [-3.05, 0.55, 1.0]
    if usePlatform:
        CSS2.theta = 0.*macros.D2R
        CSS2.setUnitDirectionVectorWithPerturbation(0., 0.)
    else:
        CSS2.nHat_B = np.array([0.0, 1.0, 0.0])

    CSS3 = coarseSunSensor.CoarseSunSensor()
    CSS3.ModelTag = "CSS3_sensor"
    setupCSS(CSS3)
    CSS3.CSSGroupID = 0
    CSS3.fov = 45.0*macros.D2R
    CSS3.r_B = [-3.05, 0.55, 1.0]
    if usePlatform:
        CSS3.theta = 90. * macros.D2R
        CSS3.setUnitDirectionVectorWithPerturbation(0., 0.)
    else:
        CSS3.nHat_B = np.array([-1.0, 0.0, 0.0])

    CSS4 = coarseSunSensor.CoarseSunSensor()
    CSS4.ModelTag = "CSS4_sensor"
    setupCSS(CSS4)
    CSS4.CSSGroupID = 0
    CSS4.r_B = [-3.05, 0.55, 1.0]
    if usePlatform:
        CSS4.theta = 180.*macros.D2R
        CSS4.setUnitDirectionVectorWithPerturbation(0., 0.)
    else:
        CSS4.nHat_B = np.array([0.0, -1.0, 0.0])

    cssList = [CSS1, CSS2, CSS3, CSS4]
    if useCSSConstellation:
        # If instead of individual CSS a cluster of CSS units is to be evaluated as one,
        # then they can be grouped into a list, and added to the Basilisk execution
        # stack as a single entity.  This is done with
        cssArray = coarseSunSensor.CSSConstellation()
        cssArray.ModelTag = "css_array"
        cssArray.sensorList = coarseSunSensor.CSSVector(cssList)
        scSim.AddModelToTask(simTaskName, cssArray)
        # Here the CSSConstellation() module will call the individual CSS
        # update functions, collect all the sensor
        # signals, and store the output in a single output message
        # containing an array of CSS sensor signals.
    else:
        # In this scenario (A) setup the CSS unit are each evaluated separately through
        # This means that each CSS unit creates a individual output messages.
        scSim.AddModelToTask(simTaskName, CSS1)
        scSim.AddModelToTask(simTaskName, CSS2)
        scSim.AddModelToTask(simTaskName, CSS3)
        scSim.AddModelToTask(simTaskName, CSS4)

    #
    #   Setup data logging before the simulation is initialized
    #
    if useCSSConstellation:
        cssConstLog = cssArray.constellationOutMsg.recorder()
        scSim.AddModelToTask(simTaskName, cssConstLog)
    else:
        css1Log = CSS1.cssDataOutMsg.recorder()
        css2Log = CSS2.cssDataOutMsg.recorder()
        css3Log = CSS3.cssDataOutMsg.recorder()
        css4Log = CSS4.cssDataOutMsg.recorder()
        scSim.AddModelToTask(simTaskName, css1Log)
        scSim.AddModelToTask(simTaskName, css2Log)
        scSim.AddModelToTask(simTaskName, css3Log)
        scSim.AddModelToTask(simTaskName, css4Log)
        
     # create the magnetic field
    magModule = magneticFieldCenteredDipole.MagneticFieldCenteredDipole()  # default is Earth centered dipole module
    magModule.ModelTag = "CenteredDipole"
    magModule.addSpacecraftToModel(scObject.scStateOutMsg)  # this command can be repeated if multiple
    simSetPlanetEnvironment.centeredDipoleMagField(magModule, 'earth')
    scSim.AddModelToTask(simTaskName, magModule)
    
    # set the simulation time
    n = np.sqrt(mu / oe.a / oe.a / oe.a)
    P = 2. * np.pi / n
    if useSphericalHarmonics:
        simulationTime = macros.sec2nano(3. * P)
    else:
        simulationTime = macros.sec2nano(3. * P)

    # Setup data logging before the simulation is initialized
    if useSphericalHarmonics:
        numDataPoints = 400
    else:
        numDataPoints = 100
    # The msg recorder can be told to sample at an with a minimum hold period in nano-seconds.
    # If no argument is provided, i.e. msg.recorder(), then a default 0ns minimum time period is used
    # which causes the msg to be recorded on every task update rate.
    # The recorder can be put onto a separate task with its own update rate.  However, this can be
    # trickier to do as the recording timing must be carefully balanced with the module msg writing
    # to avoid recording an older message.
    samplingTime = unitTestSupport.samplingTime(simulationTime, simulationTimeStep, numDataPoints)
    magLog = magModule.envOutMsgs[0].recorder()#samplingTime)
    scSim.AddModelToTask(simTaskName, magLog)
    # create a logging task object of the spacecraft output message at the desired down sampling ratio
    dataRec = scObject.scStateOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, dataRec)
    
    if liveStream:
        clockSync = simSynch.ClockSynch()
        clockSync.accelFactor = 50.0
        scSim.AddModelToTask(simTaskName, clockSync)

        # if this scenario is to interface with the BSK Viz, uncomment the following line
        viz = vizSupport.enableUnityVisualization(scSim, simTaskName, scObject
                                            , liveStream=True, cssList=CSS1
                                            )
        vizSupport.setInstrumentGuiSetting(viz, viewCSSPanel=True, viewCSSCoverage=True, showCSSLabels=True)

    #
    #   initialize Simulation:  This function clears the simulation log, and runs the self_init()
    #   cross_init() and reset() routines on each module.
    #   If the routine InitializeSimulationAndDiscover() is run instead of InitializeSimulation(),
    #   then the all messages are auto-discovered that are shared across different BSK threads.
    #
    scSim.InitializeSimulation()

    #
    #   configure a simulation stop time and execute the simulation run
    #
    scSim.ConfigureStopTime(simulationTime)
    scSim.ExecuteSimulation()

    #
    #   retrieve the logged data
    #
    posData = dataRec.r_BN_N
    velData = dataRec.v_BN_N
    magData = magLog.magField_N

    np.set_printoptions(precision=16)
    
    # When the simulation completes 2 plots are shown for each case.  One plot always shows
    # the inertial position vector components, while the second plot either shows a planar
    # orbit view relative to the peri-focal frame (no spherical harmonics), or the
    # semi-major axis time history plot (with spherical harmonics turned on).
    figureList, finalDiff = plotOrbits(dataRec.times(), posData, velData, oe, mu, P,
                            orbitCase, useSphericalHarmonics, planetCase, planet)
    
    dataCSSArray = []
    dataCSS1 = []
    dataCSS2 = []
    dataCSS3 = []
    dataCSS4 = []
    if useCSSConstellation:
        dataCSSArray = cssConstLog.CosValue[:, :len(cssList)]
    else:
        dataCSS1 = css1Log.OutputData
        dataCSS2 = css2Log.OutputData
        dataCSS3 = css3Log.OutputData
        dataCSS4 = css4Log.OutputData
    np.set_printoptions(precision=16)

    # # Export Results for solar-sim
    import json
    css1sanitized = []
    css2sanitized = []
    css3sanitized = []
    css4sanitized = []
    for val in css1Log.OutputData.tolist():
        css1sanitized.append(int(val))
    for val in css2Log.OutputData.tolist():
        css2sanitized.append(int(val))
    for val in css3Log.OutputData.tolist():
        css3sanitized.append(int(val))
    for val in css4Log.OutputData.tolist():
        css4sanitized.append(int(val))
    out_dict = {0: css1sanitized, 1: css2sanitized, 2: css3sanitized, 3: css4sanitized}
    # print(out_dict[0][0:10])
    json_object = json.dumps(out_dict, indent=4)
    
    with open('out.json', 'w') as outfile:
        outfile.write(json_object)
        
        
    # Export Results for HC
    em_data = []
    
    print(magData[1]*1e6)
    

    #
    #   plot the results
    #
    fileNameString = os.path.basename(os.path.splitext(__file__)[0])
    plt.close("all")        # clears out plots from earlier test runs
    plt.figure(1)
    if useCSSConstellation:
        for idx in range(len(cssList)):
            plt.plot(cssConstLog.times()*macros.NANO2SEC, dataCSSArray[:, idx],
                         color=unitTestSupport.getLineColor(idx,3),
                         label='CSS$_{'+str(idx)+'}$')
    else:
        timeAxis = css1Log.times()
        plt.plot(timeAxis * macros.NANO2SEC, dataCSS1,
                 color='#0000ff',
                 label='CSS$_{1}$')
        plt.plot(timeAxis * macros.NANO2SEC, dataCSS2,
                 color='#00ff00',
                 label='CSS$_{2}$')
        plt.plot(timeAxis * macros.NANO2SEC, dataCSS3,
                 color='#ff0000',
                 label='CSS$_{3}$')
        plt.plot(timeAxis * macros.NANO2SEC, dataCSS4,
                 color='#aaaaaa',
                 label='CSS$_{4}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [sec]')
    plt.ylabel('CSS Signals ')
    figureList = {}
    pltName = fileNameString+str(int(useCSSConstellation))+str(int(usePlatform))+str(int(useEclipse))+str(int(useKelly))
    figureList[pltName] = plt.figure(1)
    
    plt.figure(2)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='sci')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    timeAxis = magLog.times() * macros.NANO2SEC
    for idx in range(3):
        plt.plot(timeAxis / P, magData[:, idx] *1e9,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label=r'$B\_N_{' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [orbits]')
    plt.ylabel('Magnetic Field [nT]')
    
    pltName = fileName + "2" + orbitCase + planetCase
    figureList[pltName] = plt.figure(2)
    
    
    if show_plots:
        plt.show()

    # close the plots being saved off to avoid over-writing old and new figures
    plt.close("all")

    return finalDiff, figureList

def plotOrbits(timeAxis, posData, velData, oe, mu, P, orbitCase, useSphericalHarmonics, planetCase, planet):
    # draw the inertial position vector components
    plt.close("all")  # clears out plots from earlier test runs
    plt.figure(1)
    fig = plt.gcf()
    ax = fig.gca()
    ax.ticklabel_format(useOffset=False, style='plain')
    finalDiff = 0.0

    for idx in range(3):
        plt.plot(timeAxis * macros.NANO2SEC / P, posData[:, idx] / 1000.,
                 color=unitTestSupport.getLineColor(idx, 3),
                 label='$r_{BN,' + str(idx) + '}$')
    plt.legend(loc='lower right')
    plt.xlabel('Time [orbits]')
    plt.ylabel('Inertial Position [km]')
    figureList = {}
    pltName = fileName + "1" + orbitCase + str(int(useSphericalHarmonics)) + planetCase
    figureList[pltName] = plt.figure(1)

    if useSphericalHarmonics is False:
        # draw orbit in perifocal frame
        b = oe.a * np.sqrt(1 - oe.e * oe.e)
        p = oe.a * (1 - oe.e * oe.e)
        plt.figure(2, figsize=np.array((1.0, b / oe.a)) * 4.75, dpi=100)
        plt.axis(np.array([-oe.rApoap, oe.rPeriap, -b, b]) / 1000 * 1.25)
        # draw the planet
        fig = plt.gcf()
        ax = fig.gca()
        if planetCase == 'Mars':
            planetColor = '#884400'
        else:
            planetColor = '#008800'
        planetRadius = planet.radEquator / 1000
        ax.add_artist(plt.Circle((0, 0), planetRadius, color=planetColor))
        # draw the actual orbit
        rData = []
        fData = []
        for idx in range(0, len(posData)):
            oeData = orbitalMotion.rv2elem(mu, posData[idx], velData[idx])
            rData.append(oeData.rmag)
            fData.append(oeData.f + oeData.omega - oe.omega)
        plt.plot(rData * np.cos(fData) / 1000, rData * np.sin(fData) / 1000, color='#aa0000', linewidth=3.0
                 )
        # draw the full osculating orbit from the initial conditions
        fData = np.linspace(0, 2 * np.pi, 100)
        rData = []
        for idx in range(0, len(fData)):
            rData.append(p / (1 + oe.e * np.cos(fData[idx])))
        plt.plot(rData * np.cos(fData) / 1000, rData * np.sin(fData) / 1000, '--', color='#555555'
                 )
        plt.xlabel('$i_e$ Cord. [km]')
        plt.ylabel('$i_p$ Cord. [km]')
        plt.grid()

        plt.figure(3)
        fig = plt.gcf()
        ax = fig.gca()
        ax.ticklabel_format(useOffset=False, style='plain')
        Deltar = np.empty((0, 3))
        E0 = orbitalMotion.f2E(oe.f, oe.e)
        M0 = orbitalMotion.E2M(E0, oe.e)
        n = np.sqrt(mu/(oe.a*oe.a*oe.a))
        oe2 = copy(oe)
        for idx in range(0, len(posData)):
            M = M0 + n * timeAxis[idx] * macros.NANO2SEC
            Et = orbitalMotion.M2E(M, oe.e)
            oe2.f = orbitalMotion.E2f(Et, oe.e)
            rv, vv = orbitalMotion.elem2rv(mu, oe2)
            Deltar = np.append(Deltar, [posData[idx] - rv], axis=0)
        for idx in range(3):
            plt.plot(timeAxis * macros.NANO2SEC / P, Deltar[:, idx] ,
                     color=unitTestSupport.getLineColor(idx, 3),
                     label=r'$\Delta r_{BN,' + str(idx) + '}$')
        plt.legend(loc='lower right')
        plt.xlabel('Time [orbits]')
        plt.ylabel('Trajectory Differences [m]')
        pltName = fileName + "3" + orbitCase + str(int(useSphericalHarmonics)) + planetCase
        figureList[pltName] = plt.figure(3)

        finalDiff = np.linalg.norm(Deltar[-1])

    else:
        plt.figure(3)
        fig = plt.gcf()
        ax = fig.gca()
        ax.ticklabel_format(useOffset=False, style='plain')
        smaData = []
        for idx in range(0, len(posData)):
            oeData = orbitalMotion.rv2elem(mu, posData[idx], velData[idx])
            smaData.append(oeData.a / 1000.)
        plt.plot(timeAxis * macros.NANO2SEC / P, smaData, color='#aa0000',
                 )
        plt.xlabel('Time [orbits]')
        plt.ylabel('SMA [km]')

    pltName = fileName + "2" + orbitCase + str(int(useSphericalHarmonics)) + planetCase
    figureList[pltName] = plt.figure(2)
    return figureList, finalDiff

if __name__ == "__main__":
    run(
        True,        # show_plots
        False,        # liveStream
        1.0,         # time step (s)
        'LEO',       # orbit Case (LEO, GTO, GEO)
        False,       # useSphericalHarmonics
        'Earth',      # planetCase (Earth, Mars)
        False,       # useCSSConstellation
        True,       # usePlatform
        True,        # useEclipse
        False        # useKelly
    )
