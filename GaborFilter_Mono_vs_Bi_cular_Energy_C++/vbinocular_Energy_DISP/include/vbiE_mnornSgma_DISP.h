#ifndef __VDISPARITY__
#define __VDISPARITY__

#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstdlib>

#include <yarp/os/all.h>
#include <yarp/sig/all.h>
#include <yarp/math/Math.h>

#include <iCub/eventdriven/all.h>
#include <iCub/eventdriven/vtsHelper.h>


#include "vGaborFilter.h"




class vDisparityManager : public yarp::os::BufferedPort<ev::vBottle>{
public:
	// vDisparityManager();
//	vDisparityManager(const int& _h, const int& _w, const int& _tempWin, const int& _orientation, const double& _threshold, const yarp::os::Bottle& _dispList);
    vDisparityManager(const int& _h, const int& _w, const int& _orientation, const yarp::os::Bottle& _dispList,  const yarp::os::Bottle& _scaleList);

	bool open(const std::string &moduleName, bool strictness = false);
	void close();
	void interrupt();

	void onRead(ev::vBottle &bot);
    bool R_cFIFO_empty =true, L_cFIFO_empty =true;

protected:
	bool strictness_;

	yarp::os::BufferedPort<ev::vBottle> outPort;
	yarp::os::BufferedPort<yarp::os::Bottle> disparityPort;
	yarp::os::BufferedPort<yarp::os::Bottle> scopeOut;


	int x_, y_, ts_;

    ev::vSurface2 *R_cFifo, *L_cFifo;

	int h_, w_, tempWin_, orientation_, fineRes_, coarseRes_, maxDisp_, minDisp_, coarseSpatialWin_, fineSpatialWin_;
    double threshold_, coarseSigma, fineSigma, coarsefs, finefs, min_evts_;

    yarp::os::Bottle dispParams_, scaleParams_;

	std::vector<double> orientationVect;
	std::vector<int> dispVect;
	std::vector<int> finedispVect;

	std::vector<std::vector<vGaborFilter> > coarseFilters;
    std::vector<std::vector<vGaborFilter> > fine_grid_Filters;
    std::vector<vGaborFilter> fineFilters, LeftFilter_Resp;

	// std::vector<std::vector<std::vector<vGaborFilter> > > coarseFilters;
	// std::vector<std::vector<vGaborFilter> > fineFilters;

	std::ofstream outDisparity;
	std::ofstream gaborResponse;
    std::ofstream gaborResponse_parameters;
    std::ofstream fgaborResponse_parameters;

    std::ofstream fgaborResponse;
    std::ofstream fine_grid_parameters;
    std::ofstream current_event_info;
    std::ofstream fcurrent_event_info;
    std::ofstream tot_event_info;

};


class vDisparityModule : public yarp::os::RFModule{
	vDisparityManager *disparityManager;

public:
	virtual bool configure(yarp::os::ResourceFinder &rf);
	virtual bool interruptModule();
	virtual bool close();
	virtual bool respond(const yarp::os::Bottle &command, yarp::os::Bottle &reply);
	virtual bool updateModule();

	virtual double getPeriod();
};

#endif // __VDISPARITY__
