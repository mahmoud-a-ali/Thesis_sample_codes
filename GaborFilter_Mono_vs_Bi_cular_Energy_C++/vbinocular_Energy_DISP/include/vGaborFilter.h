#ifndef __VGABORFILTER__
#define __VGABORFILTER__

#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <cstring>

#include <utility>

#include <iCub/eventdriven/all.h>
#include <opencv2/opencv.hpp>

class vGaborFilter{

public:
	vGaborFilter();
	vGaborFilter(const int& _cx, const int& _cy, const double& _freqSpatial, const double& _varSpatial, const double& _orientation, const int& _disp);

	virtual ~vGaborFilter();

	void setCenter(const int& _cx, const int& _cy);
	void setFreq(const double& _freqSpatial);
	void setVar(const double& _varSpatial);
	void setOrientation(const double& _orientation);
	void setDisp(const int& _disp);
	void setParams(const int& _cx, const int& _cy, const double& _freqSpatial, const double& _varSpatial, const double& _orientation, const int& _disp);

	void process(ev::event<ev::AE> evt, double gain, int pol);
	void process(ev::vQueue& q, double gain, int pol);

    std::pair<double, double> getResponse();

    double getMonoResponse();
	double getOrientation();
	int getDisp();
	void reset();

protected:
	double freqSpatial_, varSpatial_, orientation_, res_, res_even_, res_odd_;
	int cx_, cy_;
	int disp_;

};

#endif // __VGABORFILTER__
