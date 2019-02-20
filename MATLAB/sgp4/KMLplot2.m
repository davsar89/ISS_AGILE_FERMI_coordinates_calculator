function KMLplot2(accesstransit)

%find number of transit access
ind=find(isnan(accesstransit(:,1)));
numAcc=length(ind)+1;

%string set up
accstr=(1:1000)';
accstr=num2str(accstr);
accstr=strcat('Access',accstr);

%file output set up
outnum=findobj('Tag','outdiredit');
OutputDirectory=get(outnum,'String');
OutputFilename='KML_Transit_Altitude_Access';
OutputDirectoryFile=strcat(OutputDirectory,'/',OutputFilename,'.kml');
fid = fopen(OutputDirectoryFile,'wt'); %open file for writing in desired directory

%write KML headers
fprintf(fid,'<kml xmlns="http://earth.google.com/kml/2.0">\n\t\t');
fprintf(fid,'<NetworkLinkControl>\n\t\t\t\t');
fprintf(fid,'<minRefreshPeriod>1</minRefreshPeriod>\n\t\t\t\t');
fprintf(fid,'<maxSessionLength>600</maxSessionLength>\n\t\t');
fprintf(fid,'</NetworkLinkControl>\n');

%set KML string variables
foldstr='<Folder>';
foldstrcl='</Folder>';
fldrname='Access Transit';
pmstr='<Placemark>';
pmstrcl='</Placemark>';
namestr='<name>';
namestrcl='</name>';
ptstr='<Point>';
ptstrcl='</Point>';
coordstr='<coordinates>';
coordstrcl='</coordinates>';
snippetstr='<Snippet maxlines="0">';
snippetstrcl='</Snippet>';
visibilstr='<visibility>';
visibilstrcl='</visibility>';
stylestr='<Style>';
stylestrcl='</Style>';
geomcolstr='<geomColor>';
geomcolstrcl='</geomColor>';
geomscalestr='<geomScale>';
geomscalestrcl='</geomScale>';
linestr='<LineString>';
linestrcl='</LineString>';
extrudestr='<extrude>';
extrudestrcl='</extrude>';
tesselstr='<tessellate>';
tesselstrcl='</tessellate>';
altmodestr='<altitudeMode>';
altmodestrcl='</altitudeMode>';
kmlcl='</kml>';


%write kml for each access
fprintf(fid,'\n%s',foldstr);
fprintf(fid,'\n\t%s%s%s',namestr,fldrname,namestrcl);
for i = 1:numAcc
    %separate kml coordinates for each access
    if i==1
        kmlcoord=accesstransit(1:ind(1)-1,2:4);
    elseif i==numAcc
        kmlcoord=accesstransit(ind(end)+1:end,2:4);
    else
        kmlcoord=accesstransit(ind(i-1)+1:ind(i)-1,2:4);
    end
    
    %write kml portion for Track
    fprintf(fid,'\n\t\t%s%s%s',namestr,fldrname,namestrcl);
    fprintf(fid,'\n\t\t%s',pmstr);
    fprintf(fid,'\n\t\t\t\t%s%s%s',namestr,accstr(i,:),namestrcl);
    fprintf(fid,'\n\t\t\t\t%s%s',snippetstr,snippetstrcl);
    fprintf(fid,'\n\t\t\t\t%s%s%s',visibilstr,'1',visibilstrcl);
    fprintf(fid,'\n\t\t\t\t%s',stylestr);
    fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',geomcolstr,'ff0000ff',geomcolstrcl);
    fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',geomscalestr,'1',geomscalestrcl);
    fprintf(fid,'\n\t\t\t\t%s',stylestrcl);
    fprintf(fid,'\n\t\t\t\t%s',linestr);
    exnum=findobj('Tag','kmlext');
    exnum1=get(exnum,'value');
    if exnum1==1
        fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',extrudestr,'1',extrudestrcl);
    else
        fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',extrudestr,'0',extrudestrcl);
    end
    fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',tesselstr,'1',tesselstrcl);
    fprintf(fid,'\n\t\t\t\t\t\t%s%s%s',altmodestr,'absolute',altmodestrcl);
    fprintf(fid,'\n\t\t\t\t\t\t%s',coordstr);
    
    %write Coordinate
    numofcoord=length(kmlcoord(:,1));
    for j=1:numofcoord
        fprintf(fid,'\n\t\t\t\t\t\t%f,%f,%f',kmlcoord(j,2),kmlcoord(j,1),kmlcoord(j,3));
    end
    fprintf(fid,'\n\t\t\t\t\t\t%s\n\t\t\t\t%s\n\t\t%s\n%s',coordstrcl,linestrcl,pmstrcl);
end
fprintf(fid,'\n%s',foldstrcl);
fprintf(fid,'\n%s',kmlcl);
fclose(fid);