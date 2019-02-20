function varargout = Documentation(varargin)
% DOCUMENTATION MATLAB code for Documentation.fig
%      DOCUMENTATION, by itself, creates a new DOCUMENTATION or raises the existing
%      singleton*.
%
%      H = DOCUMENTATION returns the handle to a new DOCUMENTATION or the handle to
%      the existing singleton*.
%
%      DOCUMENTATION('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in DOCUMENTATION.M with the given input arguments.
%
%      DOCUMENTATION('Property','Value',...) creates a new DOCUMENTATION or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before Documentation_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to Documentation_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help Documentation

% Last Modified by GUIDE v2.5 23-Jan-2018 11:08:47

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @Documentation_OpeningFcn, ...
                   'gui_OutputFcn',  @Documentation_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before Documentation is made visible.
function Documentation_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to Documentation (see VARARGIN)

% Choose default command line output for Documentation
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes Documentation wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = Documentation_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in list.
function list_Callback(hObject, eventdata, handles)
% hObject    handle to list (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns list contents as cell array
%        contents{get(hObject,'Value')} returns selected item from list


% --- Executes during object creation, after setting all properties.
function list_CreateFcn(hObject, eventdata, handles)
% hObject    handle to list (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in open.
function open_Callback(hObject, eventdata, handles)
% hObject    handle to open (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

x = get(handles.list,'value');

if x==1
    winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/ANSIC63.12-2015.pdf');
elseif x==2
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/NAWCWD TP 8347.pdf');
elseif x==3
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/C95.1-2345 2014.pdf');
elseif x==4
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/OP 3565 (18th revision).pdf');
elseif x==5
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/IRIG106 AppendixA.pdf');
elseif x==6
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/HDBK 235C 2010.pdf');
elseif x==7
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/1987_12_29_MIL_HDBK_419A_GroundBonding.pdf');
elseif x==8
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/MIL-STD-464C.pdf');
elseif x==9
        winopen('C:\E3MAT\v717\runtime\win64\Other Documentation/MIL-STD-461G.pdf');
end
