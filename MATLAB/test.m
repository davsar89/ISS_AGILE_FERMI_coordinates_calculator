clearvars
close all
clc

%%
addpath('./lib/');
addpath('./sgp4/');

%%
% if not present, the script build_TLE_structure.m should be called first to generate /dataFiles/TLE_struct.mat
TLE_struct=load('../dataFiles/TLE_struct.mat');
TLE_struct=TLE_struct.TLE_struct;

%% wanted time

% TGF-190324-00:31:52-33518
time_datetime = datetime(2019,3,24,0,31,52,335.18); % required time

%% ISS
[lat_i,long_i,alt_i] = satellite_coordinates(time_datetime,TLE_struct.ISS) % output are geodetic latitude, longitude and height (~altitude)

%% Fermi
[lat_f,long_f,alt_f] = satellite_coordinates(time_datetime,TLE_struct.Fermi) % output are geodetic latitude, longitude and height (~altitude)

%% AGILE
[lat_a,long_a,alt_a] = satellite_coordinates(time_datetime,TLE_struct.AGILE) % output are geodetic latitude, longitude and height (~altitude)

%% distances 
wgs84 = wgs84Ellipsoid('meters');
[arclen_f,~] = distance(lat_i,long_i,lat_f,long_f,wgs84);
arclen_f = arclen_f/1000 % m to km

wgs84 = wgs84Ellipsoid('meters');
[arclen_a,~] = distance(lat_i,long_i,lat_a,long_a,wgs84);
arclen_a = arclen_a/1000 % m to km
