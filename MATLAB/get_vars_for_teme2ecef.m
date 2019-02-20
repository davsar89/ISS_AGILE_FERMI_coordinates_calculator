function [ttt,jdut1,lod,xp,yp] = get_vars_for_teme2ecef(datetime_in)

%Get vars for teme2ecef
convrt = pi / (3600.0*180.0); %arc sec to rad
convrtm= (0.001*pi) /(180.0*3600.0);
% xp=.0075*convrt;
% yp=.2925*convrt; %xp and yp from Naval observatory, 1/26/2016
% lod=0; %Excess length of day
% dut1=0;
% dat=0;
timezone=0;

year_str = sprintf('%02d',year(datetime_in));
month_str = sprintf('%02d',month(datetime_in));
day_str = sprintf('%02d',day(datetime_in));

date_str_in = [year_str ' ' month_str ' ' day_str];

%Sean Kim edit
startdatestr = datestr(date_str_in,'yyyy mm dd');

pathname='../dataFiles/';
filename='EOP-short.txt';

fid = fopen(fullfile(pathname,filename));
datastartstr = 'BEGIN OBSERVED';
while 1
    tline = fgetl(fid);
    if(strcmp(datastartstr,tline))
        break;
    end
end
while 1
    tline = fgetl(fid);
    if(~isempty(tline))
        if(strcmp(startdatestr,tline(1:10)))
            break;
        end
    end
end
eopdata = tline;
xp = str2num(eopdata(18:26))*convrt;
yp = str2num(eopdata(28:36))*convrt;
dut1 = str2num(eopdata(38:47));
lod = str2num(eopdata(49:58));
% dPsi = str2num(eopdata(60:68));
% dEpsilon = str2num(eopdata(70:78));
% dx = str2num(eopdata(80:88));
% dy = str2num(eopdata(90:98));
dat = str2num(eopdata(100:102));

%%
    yearr=year(datetime_in);
    monn=month(datetime_in);
    dayy=day(datetime_in);
    hrr=hour(datetime_in);
    minn=minute(datetime_in);
    secc=second(datetime_in);
    
    [ut1, tut1, jdut1, utc, tai, tt, ttt, jdtt, tdb, ttdb, jdtdb, tcg, jdtcg, tcb, jdtcb ] ...
        = convtime ( yearr, monn, dayy, hrr, minn, secc, timezone, dut1, dat );
    

%     [recef,vecef,aecef] = teme2ecef  ( r(i,:)',v(i,:)',a(i,:)',ttt,jdut1,lod,xp,yp );

end