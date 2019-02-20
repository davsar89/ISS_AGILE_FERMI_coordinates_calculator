%This function finds the ground range, slant range, and elevation 
%of the geodetic horizon along 0 deg True from an observers location

function [HorEl, ElSR, ElGR] = GeoHorizonEl (lat1,lon1,alt1)

wgs84=[6378.137 0.081819190842622];
wgs8443=[8504.182667 0.081819190842622]; %Used for radar horizon (4/3r earth)

rng=.1:.1:10000; %km
srng=size(rng);
rngvec=ones(1,srng(2));
rngvec2=zeros(1,srng(2));
rngvec3=alt1*ones(1,srng(2));


nnaz=0*rngvec; %Find horizon at 0 deg True
hlat=lat1*rngvec;
hlon=lon1*rngvec;
halt=alt1*rngvec;
% 
% 
% dat=get(handles.gps1,'Value');
% if (dat==0)
%     %Correct alt1 for geoid if MSL
%     z = ltln2val(datagrid,refvec,lat1,lon1,'bilinear'); %geoid height at pt1
%     alt1=alt1+z/1000; %Height above ellipsoid
% else %check to make sure altitude is above geoid
%     z = ltln2val(datagrid,refvec,lat1,lon1,'bilinear');
%     if(alt1<z/1000)
%         errordlg('GPS altitude is below geoid!');
%         return
%     end
% end



%Determine elevation of horizon
[lato, lono] = reckon(hlat',hlon', rng', nnaz', wgs84);

%Get geoid altitude along reckoned path
% geoalts = ltln2val(datagrid,refvec,lato,lono,'bilinear');

[e,sr,adum]=elevation(hlat',hlon',halt',lato,lono,rngvec2','degrees',wgs84);

% [e,sr]=elevation(hlat',hlon',halt',lato,lono,rngvec2','degrees',wgs84);

HorEl=max(e);

%line is the line that that is maximum elevation for horizon
line=find(e==HorEl);

%%ddmax is distance to horizon elevation max, 0 altitude
ElSR=sr(line); %km

dist=distance(hlat',hlon',lato,lono,wgs84);

ElGR=dist(line);