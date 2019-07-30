#include "vbiE_mnornSgma_DISP.h"

bool vDisparityModule::configure(yarp::os::ResourceFinder &rf){
    //set the name of the module
    yarp::os::RFModule::setName(rf.check("name", yarp::os::Value("vDisparity")).asString().c_str());

    // std::string moduleName =
    // rf.check("name", yarp::os::Value("vDisparity")).asString();
    // yarp::os::RFModule::setName(moduleName.c_str());

    bool strictness = rf.check("strict", yarp::os::Value(true)).asBool();

    /* create the thread and pass pointers to the module parameters */
    disparityManager = new vDisparityManager( rf.check("width", yarp::os::Value(304)).asInt(),
                                              rf.check("height", yarp::os::Value(240)).asInt(),
                                              rf.check("orientation", yarp::os::Value(8)).asInt(),
                                              rf.findGroup("disparity"),
                                              rf.findGroup("scale")); //thrshold was 0.000001

    return disparityManager->open(getName(), strictness);
}

bool vDisparityModule::interruptModule(){
    disparityManager->interrupt();
    yarp::os::RFModule::interruptModule();
    return true;
}

bool vDisparityModule::close(){
    disparityManager->close();
    delete disparityManager;
    yarp::os::RFModule::close();
    return true;
}

bool vDisparityModule::updateModule(){
    return true;
}

double vDisparityModule::getPeriod(){
    return 0.1;
}

bool vDisparityModule::respond(const yarp::os::Bottle &command, yarp::os::Bottle &reply){
    return true;
}


//========================================================================================
vDisparityManager::vDisparityManager(const int& _h, const int& _w, const int& _orientation, const yarp::os::Bottle& _dispList, const yarp::os::Bottle& _scaleList){

    this->h_ = _h;
    this->w_ = _w;
    this->orientation_ = _orientation;
    this->dispParams_  = _dispList;
    this->scaleParams_ = _scaleList;

    this->maxDisp_    = dispParams_.find("maxDisp").asInt();
    this->minDisp_    = dispParams_.find("minDisp").asInt();
    this->coarseRes_  = dispParams_.find("coarseRes").asInt();
    this->fineRes_    = dispParams_.find("fineRes").asInt();
    this->tempWin_    = dispParams_.find("tmpW").asInt();
    this->threshold_  = dispParams_.find("thrshld").asDouble();
    this->min_evts_   = dispParams_.find("min_evts").asDouble();

    this->coarseSpatialWin_  = scaleParams_.find("spW").asInt();
    this->coarseSigma        = scaleParams_.find("sgma").asDouble();
    this->coarsefs           = scaleParams_.find("spF").asDouble();

    this->fineSpatialWin_    = scaleParams_.find("finespW").asInt();
    this->fineSigma          = scaleParams_.find("finesgma").asDouble();
    this->finefs             = scaleParams_.find("finespF").asDouble();


    for(int i=minDisp_; i<=maxDisp_; i+=coarseRes_){
        dispVect.push_back(i);
    }


    std::cout<<"Min,Max disp.     : "<<minDisp_ << ",  " <<maxDisp_<<std::endl;
    std::cout<<"coarse SpW        : "<<coarseSpatialWin_<<std::endl;
    std::cout<<"coarse Sigma      : "<<coarseSigma <<std::endl;
    std::cout<<"coarse spF        : "<< coarsefs<<std::endl;
    std::cout<<"fine SpW          : "<<fineSpatialWin_<<std::endl;
    std::cout<<"fine Sigma        : "<<fineSigma <<std::endl;
    std::cout<<"fine spF          : "<< finefs<<std::endl;
    std::cout<<"tmpW              : "<<tempWin_<<std::endl;
    std::cout<<"Events limit      : "<<min_evts_<<std::endl;
    std::cout<<"Threshold         : "<<threshold_<<std::endl;


    //set up coarse filters
    for(int i=0;i<orientation_;i++){
        double angle = (double)i/(double)orientation_*M_PI;
        orientationVect.push_back(angle);
        std::vector<vGaborFilter> row;
        for(unsigned int j=0;j<dispVect.size();j++){
            vGaborFilter gf(w_/2, h_/2, coarsefs, coarseSigma, angle, dispVect[j]);
            row.push_back(gf);

        }
        coarseFilters.push_back(row);
    }



    //set up fine filters
    for(int i= (int)(- coarseRes_ + fineRes_-1)/2;i<(int)(coarseRes_+ fineRes_+1)/2;i+=fineRes_){
        vGaborFilter gf(0,0, finefs,  fineSigma, 0, 0);//replace sigma
        finedispVect.push_back(i);
        fineFilters.push_back(gf);
    }


    //set up leftFilter Resp
    for(int i=0; i<= orientationVect.size(); i++){
        vGaborFilter gf(0,0, finefs,  fineSigma, orientationVect[i], 0);//replace sigma, finefreq=finefs
        LeftFilter_Resp.push_back(gf);
    }

    /******/
    std::cout << "orient_vector: " ;
    for (int i=0; i<orientationVect.size();i++){
        std::cout << orientationVect[i] <<",  ";
    }
    std::cout << std::endl;

    std::cout << "disp_vector: " ;
    for (int i=0; i<dispVect.size();i++){
        std::cout << dispVect[i] <<",  ";
    }
    std::cout << std::endl;

    std::cout << "fine_disp_vector: " ;
    for (int i=0; i<finedispVect.size();i++){
        std::cout << finedispVect[i] <<",  ";
    }
    std::cout << std::endl;

    /****************/





    R_cFifo = new ev::temporalSurface(w_, h_, tempWin_);
    L_cFifo = new ev::temporalSurface(w_, h_, tempWin_);
    // cFifo = new ev::fixedSurface(50, w_, h_);

    outDisparity.open("estimatedDisparity.txt");
    //-------------------------------------------------------------
    // store parameters for matlab:
    for (int i=0; i<dispVect.size();i++){
        gaborResponse_parameters<< dispVect[i] <<" ";
    }
    gaborResponse_parameters<<"\n";

    for (int i=0; i<orientationVect.size();i++){
        gaborResponse_parameters<< orientationVect[i] <<" ";
    }
    for (int i=orientationVect.size(); i<dispVect.size();i++){
        gaborResponse_parameters<< 000 <<" ";
    }
    gaborResponse_parameters<<"\n";
}

bool vDisparityManager::open(const std::string &moduleName, bool strictness){
    this->strictness_ = strictness;
    if(strictness){
        std::cout<<"Setting " <<moduleName<<" to strict"<<std::endl;
        this->setStrict();
    }

    this->useCallback();

    if(!yarp::os::BufferedPort<ev::vBottle>::open("/" + moduleName + "/vBottle:i"))
        return false;

    if(!outPort.open("/" + moduleName + "/vBottle:o"))
        return false;

    if(!scopeOut.open("/" + moduleName + "/scope:o"))
        return false;

    if(!disparityPort.open("/"+moduleName + "/disp:o"))
        return false;

    return true;
}

void vDisparityManager::close(){


    outDisparity.close();
    outPort.close();
    scopeOut.close();
    yarp::os::BufferedPort<ev::vBottle>::close();
}

void vDisparityManager::interrupt(){
    outPort.interrupt();
    scopeOut.interrupt();
    yarp::os::BufferedPort<ev::vBottle>::interrupt();
}

void vDisparityManager::onRead(ev::vBottle &bot){
    std::cout  <<  " OnRead  " << std::endl;
    ev::vBottle &outBottle = outPort.prepare();
    outBottle.clear();
    yarp::os::Stamp st;
    this->getEnvelope(st);
    outPort.setEnvelope(st);

    ev::vQueue wL, wR;

    ev::vQueue q = bot.get<ev::AE>();
    int x, y, ts, pol, ch;
    yarp::os::Bottle &scopebot = scopeOut.prepare();
    scopebot.clear();

    for(ev::vQueue::iterator qi = q.begin(); qi!=q.end(); qi++){
        auto aep = ev::is_event<ev::AE>(*qi);
        //        std::cout  << aep->stamp << "  " << aep->channel << "  "<< aep->x << "  " << aep->y << "  " << aep->polarity << std::endl;

        /************************ for only address events *************/
        if(!aep)
            continue;

        /*************** add events in window **************/
        if(aep->getChannel()){
            R_cFifo->addEvent(aep);
            continue;
        }else
            L_cFifo->addEvent(aep);

        //  std::cout<<"waiting new event ........................................."<<std::endl;
        x = aep->x;
        y = aep->y;
        pol = aep->polarity;
        ts = aep->stamp;
        ch = aep->channel;


        //      std::cout  << "all condition correct " << aep->channel << " " << x << " " << y << std::endl;
        double coarse_ori=0.0;
        int orn_idx=0, coarse_disp=0.0;
        double dispX=0.0;
        double dispY=0.0;
        bool coarseCheck = false;
        bool fineCheck = false;
        double minE_ovr_frq = threshold_ ;

        int fine_disp=0.0;
        std::vector<double> L_even_resp , L_odd_resp ;
        L_even_resp.resize(8); L_odd_resp.resize(8);
        double even_rsp, odd_rsp, L_even_rsp, L_odd_rsp  ;
        std::pair<double,double> oddeven_resp;
        oddeven_resp.first=0;   oddeven_resp.second=0;
        double E_ovr_frq=0;

         /************************************************************************************************************************************/
        /**************************************************** Left response odd and even  ***************************************************/
        /************************************************************************************************************************************/
        //compute monocular energy from left events
        wL.clear();
        wL = L_cFifo->getSurf(x, y, coarseSpatialWin_);
        if( wL.size() < min_evts_){
            //std::cout <<" less than expected events in lW "<< wL.size() << std::endl;
            continue;
        }

        bool E_check = false;
        /********************************* orientation loop for left response ******************************/
//        std::cout<< "left resp wrt orn:";
        for(unsigned int i=0; i<orientationVect.size(); i++){
            std::fill(L_even_resp.begin(), L_even_resp.end(), 0.0);
            std::fill(L_even_resp.begin(), L_even_resp.end(), 0.0);
            L_even_rsp=0;   L_odd_rsp=0;
            even_rsp=0,   odd_rsp=0;
            minE_ovr_frq = 0.01;
            /********************************* freq loop for ******************************/
            for(unsigned int sgm=1; sgm<4; sgm++){
                for(unsigned int frq=1; frq<9; frq++){
                    LeftFilter_Resp[i].reset();
                    LeftFilter_Resp[i].setVar(sgm*coarseSigma);
                    LeftFilter_Resp[i].setFreq(frq*coarsefs);
                    LeftFilter_Resp[i].setCenter(x,y);
                    LeftFilter_Resp[i].setDisp(0.0); //it is already zero
                    LeftFilter_Resp[i].process(wL,1.0,pol); //gain = 1.0
                    oddeven_resp = LeftFilter_Resp[i].getResponse();
                    even_rsp = even_rsp + fabs(oddeven_resp.first); //no it should be halfwave rectifiered
                    odd_rsp  = odd_rsp + fabs(oddeven_resp.second);
                }
            }
            /********************************* end of freq loop ******************************/
            E_ovr_frq = pow(even_rsp,2) + pow(odd_rsp,2); //monoresp just to check of the response is greater than the limit
            if(E_ovr_frq > minE_ovr_frq){
                E_check = true;
                minE_ovr_frq= E_ovr_frq;
                L_even_rsp = even_rsp;
                L_odd_rsp = odd_rsp;
                orn_idx = i;
                coarse_ori = orientationVect[orn_idx];
            }
        } //std::cout<< std::endl;
        /*********************************end of orn loop ******************************/
        if (E_check == false)
            continue;

/************************************************************************************************************************************/
/********************************************** coarse loop for Right events ********************************************************/
/************************************************************************************************************************************/
        coarseCheck = false;
        minE_ovr_frq= threshold_;
        /******************************************************* disparity loop ***************************************************/
        for(unsigned int j=0; j<dispVect.size(); j++){
            wR.clear();
            wR = R_cFifo->getSurf(x+dispVect[j], y, coarseSpatialWin_);  //why define it inside loop, it assign it here not define
            if( wR.size() <  (wL.size()-(wL.size()/5) )  ){
//                std::cout <<"diff not cosistent: WL: "<< wL.size() <<",   WR: "<<  wR.size() << ",   diff "<<  abs( wL.size()-wR.size() ) << ",   diff thrshld "<<  (wL.size()/5)  <<std::endl;
                continue;
            }
            if( wR.size() >  (wL.size()+(wL.size()/5) )  ){
//                std::cout <<"diff not cosistent: WL: "<< wL.size() <<",   WR: "<<  wR.size() << ",   diff "<<  abs( wL.size()-wR.size() ) << ",   diff thrshld "<<  (wL.size()/5)  <<std::endl;
                continue;
            }
                // no orn loop we take it from the mono energy
                even_rsp=0;  odd_rsp=0; E_ovr_frq=0;
                /***************************Frequency loop**************************/
                for(unsigned int sgm=1; sgm<4; sgm++){
                    for(unsigned int frq=1; frq<9; frq++){ //max 4sigma i think
                        coarseFilters[orn_idx][j].reset();
                        coarseFilters[orn_idx][j].setFreq(frq*coarsefs);
                        coarseFilters[orn_idx][j].setVar(sgm*coarseSigma);
                        coarseFilters[orn_idx][j].setCenter(x,y);
                        coarseFilters[orn_idx][j].setDisp(dispVect[j]);
                        coarseFilters[orn_idx][j].process(wR,1.0,pol);
                        oddeven_resp = coarseFilters[orn_idx][j].getResponse();
                        even_rsp = even_rsp + fabs(oddeven_resp.first);
                        odd_rsp  = odd_rsp + fabs(oddeven_resp.second);
                    }
                }
                /************************end of Frequency loop **********************/
                  E_ovr_frq = (L_even_rsp + even_rsp)*(L_even_rsp + even_rsp) + (L_odd_rsp+ odd_rsp)*(L_odd_rsp + odd_rsp) ;
//                std::cout <<"disp  "<< dispVect[j] <<":   " <<  E_ovr_frq ;

                if(E_ovr_frq > minE_ovr_frq){
                    coarseCheck = true;
                    minE_ovr_frq= E_ovr_frq;
                    coarse_disp = dispVect[j];
                }
        }
        /****************************************************** end of disp loop ************************************************/

/*****************************************************************************************************************/
/********************************************** Fine Grid ********************************************************/
/*****************************************************************************************************************/
        if(coarseCheck)
        {
            minE_ovr_frq = threshold_;  //reset it for every orn
            /*********************************** disp loop **************************************/
            for(unsigned int j=0; j<finedispVect.size();j++){
                if(abs(coarse_disp + finedispVect[j])> maxDisp_)
                    continue;
                wR.clear();
                wR = R_cFifo->getSurf(x+coarse_disp+finedispVect[j], y, fineSpatialWin_);
                even_rsp=0;  odd_rsp=0 ;
                /***************************Frequency loop**************************/
                for(unsigned int sgm=1; sgm<4; sgm++){
                    for(unsigned int frq=1; frq<9; frq++){ //max 4sigma i think
                        fineFilters[orn_idx].reset();
                        fineFilters[orn_idx].setVar(sgm*coarseSigma);
                        fineFilters[orn_idx].setFreq(frq*finefs);
                        fineFilters[orn_idx].setCenter(x,y);
                        fineFilters[orn_idx].setDisp(coarse_disp + finedispVect[j]);
                        fineFilters[orn_idx].process(wR,1.0,pol);
                        oddeven_resp = fineFilters[orn_idx].getResponse();
                        even_rsp = even_rsp + fabs(oddeven_resp.first);
                        odd_rsp  = odd_rsp + fabs(oddeven_resp.second);
                    }
                }
                /************************end of Frequency loop **********************/
                E_ovr_frq = (L_even_rsp+ even_rsp)*(L_even_rsp + even_rsp) + (L_odd_rsp + odd_rsp)*(L_odd_rsp + odd_rsp) ;
                if(E_ovr_frq > minE_ovr_frq){
                    fineCheck = true;
                    minE_ovr_frq= E_ovr_frq;
                    fine_disp = coarse_disp + finedispVect[j];
                }
//                std::cout<<"disp "<< j<< ": "<< E_ovr_frq << std::endl;
            }
        /*********************************** end of disp loop ********************************************/
   }
/********************************************** end of Fine Grid ********************************************************/
            if(coarseCheck && fineCheck){  //){//&& fineCheck){
                dispX = fine_disp;
                outDisparity << x << " " << y << " " << ts << " " << dispX << " " << dispY<<"\n";
                std::cout << dispX << std::endl; //<<"disparity event"
                auto de = ev::make_event<ev::DisparityEvent>(aep);
                de->dx = dispX;
                de->dy = dispY;
                outBottle.addEvent(de);
            }
    }
/**************************************************** end of iterator qi ***********************************************************/

    if(strictness_){
        outPort.writeStrict();
    }
    else{
        outPort.write();
    }


}
