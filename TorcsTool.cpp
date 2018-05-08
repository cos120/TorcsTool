//
// Created by zj on 17-6-21.
//

#include <iostream>
#include <unistd.h>
#include <sys/shm.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

using namespace std;

#define image_width 640
#define image_height 480

struct env_to_read{

	double steer;
	double brake;
	double accel;
	int gear;
	double clutch;
	double speed_x;
	double speed_y;
	double speed_z;
	double track_pos;
	double track_angle;

	double rpm;
	double radius;
};

struct env_to_read_29{
	float angle_dqn;
	float track_dqn[19];
	float track_pos_dqn;
	float speed_x_dqn;
	float speed_y_dqn;
	float speed_z_dqn;
	float wheel_dqn[4];
	float rpm_dqn;
};

struct env_to_write{

	bool is_restart;
	double steer;
	double brake;
	double accel;
	int gear;
	double clutch;


};
struct shared_use_st
{
    int written;
    uint8_t data[image_width*image_height*3];
    int pause;
    int zmq_flag;
    int save_flag;

    struct env_to_write env_write;
	struct env_to_read env_read;
    bool is_ready;
    bool is_hit_wall;
	bool is_finish;
	bool is_stuck;
    struct env_to_read_29 env_read_29;
    bool dqn_ready;

};


class TorcsTool{
private:
    void *shm = NULL;
    bool flg;
    struct shared_use_st *shared;

public:
    TorcsTool(int key){
        int shmid = shmget((key_t)key, sizeof(struct shared_use_st),0666| IPC_CREAT);
        flg = true;
        if(shmid == -1){
            cout<<"error in shmget"<<endl;
        }

        shm = shmat(shmid, NULL, 0);
        if(shm ==  (void*)-1){
            cout<<"error in shmat"<<endl;
        }
        shared                               = (struct shared_use_st*)shm;
        shared->written                      = 0;
        shared->pause                        = 0;
        shared->zmq_flag                     = 0;
        shared->save_flag                    = 0;

        shared->env_write.is_restart         = false;
        shared->env_write.steer              = 0;
        shared->env_write.brake              = 0;
        shared->env_write.accel              = 0;
        shared->env_write.gear               = 1;
        shared->env_write.clutch             = 0;

        shared->env_read.speed_x             = 0;
        shared->env_read.speed_y             = 0;
        shared->env_read.speed_z             = 0;
        shared->env_read.steer               = 0;
        shared->env_read.brake               = 0;
        shared->env_read.accel               = 0;
        shared->env_read.gear                = 0;
        shared->env_read.clutch              = 0;
        shared->env_read.track_angle         = 0;

        shared->env_read.track_pos           = 0;
        shared->env_read.rpm                 = 0;
        shared->env_read.radius              = 0;
        shared->is_ready                     = false;
        shared->is_hit_wall                  = false;
        shared->is_finish                    = false;
        shared->is_stuck                     = false;

        shared->env_read_29.angle_dqn        = 0;
        shared->env_read_29.track_pos_dqn    = 0;
        shared->env_read_29.speed_x_dqn      = 0;
        shared->env_read_29.speed_y_dqn      = 0;
        shared->env_read_29.speed_z_dqn      = 0;
        shared->env_read_29.rpm_dqn          = 0;
        shared->dqn_ready                    = false;

//        printf("\n********** Memory sharing started, attached at %X **********\n", shm);
    }


    void reverseGetImageFlag(){ shared->pause = 1 - shared->pause; }
    void restart(){ shared->env_write.is_restart = true; }
    void stop(){ flg = false; }


    void setGear(int _gear){ shared->env_write.gear = _gear;}
    void setClutch(double _clutch){ shared->env_write.clutch = _clutch;}
    void setAccel(double _accel){ shared->env_write.accel = _accel;}
    void setSteer(double _steer){ shared->env_write.steer = _steer;}
    void setBrake(double _brake){ shared->env_write.brake = _brake;}
    void clearHitWall(){shared->is_hit_wall = false;}
    void clearFinish(){shared->is_finish = false;}
    void clearStuck(){shared->is_stuck = false;}

    bool isHitWall(){return shared->is_hit_wall;}
    bool isFinish(){return shared->is_finish;}
    bool isStuck(){
        if(shared->is_ready){
            return shared->is_stuck;
        }else{
            return false;
        }
    }
    double getTrackAngle(){return shared->env_read.track_angle;}
    double getSpeed(){ return shared->env_read.speed_x;}
    double getSpeed_y(){ return shared->env_read.speed_y;}
    double getSpeed_z(){ return shared->env_read.speed_z;}
    double getRpm(){ return shared->env_read.rpm;}
    double getTrackPos(){ return shared->env_read.track_pos;}
    double getRadius(){ return shared->env_read.radius;}
    double getBrake(){ return shared->env_read.brake; }
    double getSteer(){ return shared->env_read.steer; }
    double getClutch(){ return shared->env_read.clutch; }
    double getAccel(){ return shared->env_read.accel; }
    int getGear(){ return shared->env_read.gear; }

    float* getTrack(){return shared->env_read_29.track_dqn; }
    float getAngle(){return shared->env_read_29.angle_dqn; }
    uint8_t* getImage(){
        while(flg){
            if(shared->written == 1){
            //printf("%s\n","123123");
                shared->written = 0;
                return shared->data;
            }
        }
    }

    env_to_read* getStruct(){
        while(true){
            if(shared->is_ready){
                shared->is_ready = false;
                return &(shared->env_read);
            }
        }
    }
    env_to_read_29* get29Data(){
        while(true){
            if(shared->dqn_ready){
                shared->dqn_ready = false;
                return &(shared->env_read_29);
            }
        }
    }
};

extern "C"{

//    TorcsTool* getTorcsTool(){return new TorcsTool();}

    TorcsTool* torcsTool = NULL;

    void init(int shared_key){
        torcsTool = new TorcsTool(shared_key);
    }

    void reserveScreenShotFlag(){torcsTool->reverseGetImageFlag();}

    void stopTorcsTool(){torcsTool->stop();}

    void restart(){torcsTool->restart();}

    void setGear( int _gear){ torcsTool->setGear(_gear); }

    void setClutch(double _clutch){ torcsTool->setClutch(_clutch);}

    void setAccel(double _accel){ torcsTool->setAccel(_accel);}

    void setSteer(double _steer){ torcsTool->setSteer(_steer);}

    void setBrake(double _brake){ torcsTool->setBrake(_brake);}

    double getTrackAngle(){torcsTool->getTrackAngle();}

    bool isHitWall(){torcsTool->isHitWall();}

    bool isFinish(){torcsTool->isFinish();}
    bool isStuck(){torcsTool->isStuck();}

    void clearHitWall(){torcsTool->clearHitWall();}

    void clearFinish(){torcsTool->clearFinish();}
    void clearStuck(){torcsTool->clearStuck();}

    uint8_t* getScreenshot(){return torcsTool->getImage();}

    double getSpeedX(){return torcsTool->getSpeed();}
    double getSpeedY(){return torcsTool->getSpeed_y();}
    double getSpeedZ(){return torcsTool->getSpeed_z();}

    double getSteer(){return torcsTool->getSteer();}

    int getGear(){return torcsTool->getGear();}

    double getBrake(){return torcsTool->getBrake();}

    double getClutch(){return torcsTool->getClutch();}

    double getAccel(){return torcsTool->getAccel();}

    double getRpm(){ return torcsTool->getRpm();}
    double getTrackPos(){ return torcsTool->getTrackPos();}
    double getRadius(){ return torcsTool->getRadius();}

    env_to_read* getStruct(){return torcsTool->getStruct();}
    env_to_read_29* get29Data(){return torcsTool->get29Data();}

    float* getTrack(){return torcsTool->getTrack();}
    float getAngle(){return torcsTool->getAngle(); }
}
