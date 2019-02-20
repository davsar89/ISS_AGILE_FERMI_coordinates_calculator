function [latgd,long,hellp] = satellite_coordinates(time_datetime,satellite_tle_info)

min_idx = find_nearest_TLE_index(time_datetime,satellite_tle_info);

tle1 = satellite_tle_info.TLE_1_list{min_idx};
tle2 = satellite_tle_info.TLE_2_list{min_idx};
best_time = satellite_tle_info.times{min_idx};

minutes_from_TLE_epoch_time = minutes(time_datetime-best_time); %calculates the number of minutes (with fraction) from TLE epoch (could be positive or negative)

[rteme, vteme] = propagation(tle1,tle2,minutes_from_TLE_epoch_time);

[ttt,jdut1,lod,xp,yp] = get_vars_for_teme2ecef(time_datetime);
ateme=[0.,0.,0.]';

[recef,vecef,aecef] = teme2ecef_2( rteme,vteme,ateme,ttt,jdut1,lod,xp,yp );

wgs84 = wgs84Ellipsoid('meters');
[latgd,long,hellp] = ecef2geodetic(wgs84,recef(1)*1000.0,recef(2)*1000.0,recef(3)*1000.0);
hellp = hellp/1000.0;

end

%%

function min_idx = find_nearest_TLE_index(wanted_datetime,sat_tle_info)

func_diff = @(t) abs(t-wanted_datetime); % function to get the time difference between all TLE times and the wanted time

A = cellfun(func_diff,sat_tle_info.times); % apply function to all elements of cell

[~,min_idx] = min(A);

end

