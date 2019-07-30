#include "vbiE_mnornSgma_DISP.h"

int main(int argc, char** argv){
	yarp::os::Network::init();

	vDisparityModule disparityModule;

	yarp::os::ResourceFinder rf;

	rf.setVerbose(true);
	rf.setDefaultContext("eMorph");
	rf.setDefaultConfigFile("tuning_params.ini");
	rf.configure(argc, argv);

	disparityModule.runModule(rf);
	yarp::os::Network::fini();

	return 0;
}
