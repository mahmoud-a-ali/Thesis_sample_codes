#include "vGaborFilter.h"


//vGaborFilter Class
vGaborFilter::vGaborFilter(){
	cx_ = 0;
	cy_ = 0;
	orientation_ = 0.0;
	freqSpatial_ = 0.0;
	varSpatial_  = 0.0;
	res_ = 0.0;
}

vGaborFilter::vGaborFilter(const int& _cx, const int& _cy, const double& _freqSpatial, const double& _varSpatial, const double& _orientation, const int& _disp){
	this->cx_ = _cx;
	this->cy_ = _cy;
	this->freqSpatial_ 	= _freqSpatial;
	this->varSpatial_ 	= _varSpatial;
	this->orientation_ 	= _orientation;
	this->disp_ = _disp;
}

vGaborFilter::~vGaborFilter(){

}

void vGaborFilter::setCenter(const int& _cx, const int& _cy){
	this->cx_ = _cx;
	this->cy_ = _cy;
}


void vGaborFilter::setFreq(const double& _freqSpatial){
	this->freqSpatial_ = _freqSpatial;
}

void vGaborFilter::setVar(const double& _varSpatial){
	this->varSpatial_ = _varSpatial;
}

void vGaborFilter::setOrientation(const double& _orientation){
	this->orientation_ = _orientation;
}

void vGaborFilter::setDisp(const int& _disp){
	this->disp_ = _disp;
}

void vGaborFilter::setParams(const int& _cx, const int& _cy, const double& _freqSpatial, const double& _varSpatial, const double& _orientation, const int& _disp){
	this->cx_ = _cx;
	this->cy_ = _cy;
	this->freqSpatial_ 	= _freqSpatial;
	this->varSpatial_ 	= _varSpatial;
	this->orientation_ 	= _orientation;
	this->disp_ = _disp;	
	// std::cout<<freqSpatial_<<"	"<<varSpatial_<<"	"<<orientation_<<"	"<<disp_<<std::endl;
}

std::pair<double, double> vGaborFilter::getResponse(){
//	return res_;
     return std::make_pair(res_even_,res_odd_);
}

double vGaborFilter::getMonoResponse(){
//	return res_;
     return res_;
}


double vGaborFilter::getOrientation(){
	return orientation_;
}

int vGaborFilter::getDisp(){
	return disp_;
}

void vGaborFilter::reset(){
	res_ = 0.0;
	res_even_ = 0.0;
	res_odd_ = 0.0;
}


void vGaborFilter::process(ev::vQueue& q, double gain, int pol){
	for(ev::vQueue::iterator wi = q.begin(); wi!= q.end(); wi++){
		auto aep = ev::is_event<ev::AE>(*wi);
		process(aep, gain, pol);
	}
}

void vGaborFilter::process(ev::event<ev::AE> evt, double gain, int pol){
    if(evt->polarity!=pol) //takes only events with same polarity
		return;
	int dx = evt->x - cx_;
	int dy = evt->y - cy_;

	double dx_theta, dy_theta;
	double G_; //envelope - gaussian function
	double S_cos, S_sin; //carrier - complex sinusoid
	double gamma = 5;
	
	dx_theta =  (dx - disp_)*cos(orientation_) + dy*sin(orientation_);
	dy_theta = -(dx - disp_)*sin(orientation_) + dy*cos(orientation_);
		
	S_cos = 1.0/(2.0*M_PI*pow(varSpatial_,2)) * cos(2*M_PI*freqSpatial_*(dx_theta));
	S_sin = 1.0/(2.0*M_PI*pow(varSpatial_,2)) * sin(2*M_PI*freqSpatial_*(dx_theta));				
	
	G_ = exp(-(gamma*pow(dx_theta,2 ) + pow(dy_theta,2))/(2*pow(varSpatial_,2)));

	res_even_ 	+= gain*G_*S_cos;
	res_odd_	+= gain*G_*S_sin;

	res_ = sqrt(pow(res_even_, 2) + pow(res_odd_, 2));
}
