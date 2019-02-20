clearvars
close all
clc

TLE_struct = [];

%% ISS

file = '../dataFiles/ISS_orbital_info.txt';

fid=fopen(file);
tline = fgetl(fid);
tlines = cell(0,1);
while ischar(tline)
    tlines{end+1,1} = tline;
    tline = fgetl(fid);
end
fclose(fid);

ISS=[];
ISS.TLE_1_list={};
ISS.TLE_2_list={};
ISS.times={};


for ii=1:2:length(tlines)
    ISS.TLE_1_list{end+1} = tlines{ii};
    ISS.TLE_2_list{end+1} = tlines{ii+1};
    
    epoch_str=ISS.TLE_1_list{end}(19:32);
    
    year_tle=str2double(epoch_str(1:2));
    if year_tle>70
        year_tle = year_tle+1900;
    else
        year_tle = year_tle+2000;
    end
    
    jday = epoch_str(1:5);
    
    integ=floor(str2double(epoch_str));
    day_fract=str2double(epoch_str)-integ;
    DOY = str2double(epoch_str(3:5));
    
    date = datetime(year_tle,1,DOY) + days(day_fract);
    
    ISS.times{end+1}=date;
end

TLE_struct.ISS=ISS;

%% Fermi

file2 = '../dataFiles/Fermi_GLAST_orbital_info.txt';

fid2=fopen(file2);
tline = fgetl(fid2);
tlines = cell(0,1);
while ischar(tline)
    tlines{end+1,1} = tline;
    tline = fgetl(fid2);
end
fclose(fid2);

Fermi=[];
Fermi.TLE_1_list={};
Fermi.TLE_2_list={};
Fermi.times={};


for ii=1:2:length(tlines)
    Fermi.TLE_1_list{end+1} = tlines{ii};
    Fermi.TLE_2_list{end+1} = tlines{ii+1};
    
    epoch_str=Fermi.TLE_1_list{end}(19:32);
    
    year_tle=str2double(epoch_str(1:2));
    if year_tle>70
        year_tle = year_tle+1900;
    else
        year_tle = year_tle+2000;
    end
    
    jday = epoch_str(1:5);
    
    integ=floor(str2double(epoch_str));
    day_fract=str2double(epoch_str)-integ;
    DOY = str2double(epoch_str(3:5));
    
    date = datetime(year_tle,1,DOY) + days(day_fract);
    
    Fermi.times{end+1}=date;
end

TLE_struct.Fermi=Fermi;



%% AGILE

file3 = '../dataFiles/AGILE_orbital_info.txt';

fid3=fopen(file3);
tline = fgetl(fid3);
tlines = cell(0,1);
while ischar(tline)
    tlines{end+1,1} = tline;
    tline = fgetl(fid3);
end
fclose(fid3);

AGILE=[];
AGILE.TLE_1_list={};
AGILE.TLE_2_list={};
AGILE.times={};


for ii=1:2:length(tlines)
    AGILE.TLE_1_list{end+1} = tlines{ii};
    AGILE.TLE_2_list{end+1} = tlines{ii+1};
    
    epoch_str=AGILE.TLE_1_list{end}(19:32);
    
    year_tle=str2double(epoch_str(1:2));
    if year_tle>70
        year_tle = year_tle+1900;
    else
        year_tle = year_tle+2000;
    end
    
    jday = epoch_str(1:5);
    
    integ=floor(str2double(epoch_str));
    day_fract=str2double(epoch_str)-integ;
    DOY = str2double(epoch_str(3:5));
    
    date = datetime(year_tle,1,DOY) + days(day_fract);
    
    AGILE.times{end+1}=date;
end

TLE_struct.AGILE=AGILE;


save('../dataFiles/TLE_struct.mat', 'TLE_struct');