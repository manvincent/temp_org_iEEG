

function [pport,pptio]= initializeLPT(pport,addr)

%  [pport]= initializeLPT(pport,addr)
%
% This function initializes access to LPT port and returns a struct with two functions,
% get and put, which respectively read and put to selected register. 
%
% On windows systems parallel port access  uses the io32 or io64 
% drivers provided by Frank Schieber: http://people.usd.edu/~schieber/psyc770/, 
% and will prompt to install the correct version if it is not detected. On
% linux systems, access requires ppMex, part of the ratrix
% toolbox released by Erik Flister, available here:
% http://ratrix.googlecode.com/archive/a9c05ae460c2ad54e51055a17838e07e90554a37.zip
%
% addr is the memory address for LPT; default is 0x378. If a file called 
% "parportaddress.txt" is in the path, then the default address will be 
% read from there. In that case the file should contain a single hexadecimal
% address number in the form 0xFFFF, where FFFF is a hexadecimal number.

% ----------- SVN REVISION INFO ------------------
% $URL$
% $Revision$
% $Date$
% $Author$
% ------------------------------------------------

if nargin < 2 || isempty(addr)
    addr ='378'; %standard address
    if exist('parportaddress.txt','file')
        %%% If a file called "parportaddress.txt" is in the path, then the
        %%% address will be read from there. The address should be in the form
        %%% 0xFFFF, where FFFF is a hexadecimal number
        fid = fopen(which('parportaddress.txt'),'r');
        str = fread(fid,'uchar=>char')';        
        fclose(fid);
        hex = regexp(str,'0x([\w\d]+)','tokens','once');
        addr = hex2dec([hex{:}]);
    end
end
if ischar(addr)
    addr=hex2dec(addr); 
end

switch lower(computer('arch'))
    
    case 'win32'
        iofun = @(varargin) io32(varargin{:});
        dllname = 'IO32';
    case 'win64'
        iofun = @(varargin) io64(varargin{:});
        dllname = 'IO64';
     case 'glnxa64'
         % First element is port number. Assuming this is 0.
         bitSpecs = (0:7)'; bitSpecs(:,2) = 0; bitSpecs = uint8(bitSpecs);
        iofun = @(varargin) ppMex(uint64([0 addr]),cat(2,bitSpecs,varargin{:}));
            dllname = 'ppMex';
%         iofun = @(varargin) pp(varargin{:});
        % dllname = 'glnxa64';
    otherwise
        error([mfilename,' only runs on win64 or win32 or linux'])
end

switch lower(computer('arch'))
    case {'win32','win64'}
        iourl ='http://apps.usd.edu/coglab/psyc770/IO32.html';

        q=which(lower(dllname));

        if isempty(q)
            error(['This script requires %s, which is not detected; make sure\n',...
                   'it is in the MATLAB path. If it has not been installed go to',...
                   '\n\n\t\t%s%s.html\n\n and follow the instructions.'],dllname,iourl,dllname)
        end


        pptio =iofun();
        iostat = iofun(pptio);
        if iostat ~=0
            error(['Problem opening LPT port. Make sure %s is properly installed.',...
                  '\nInstructions are here:\n\n%s%s.html\t\t'],dllname,iourl,dllname)
        end

        pport.get =@()iofun(pptio,addr);
        pport.put =@(x)iofun(pptio,addr,x);
        pport.obj = pptio;
    case 'glnxa64'
        
        url = 'http://ratrix.googlecode.com/archive/a9c05ae460c2ad54e51055a17838e07e90554a37.zip';
        if ~exist('ppMex','file')
               error(['This script requires %s to interface with the parallel port, which is not detected; make sure\n',...
                   'it is in the MATLAB path. If it has not been installed download',...
                   '\n\n\t\t%s\n\n and follow the instructions to compile and install.'],dllname,url)     
        end
%         pptio = uint8(2:9);
         dec2logic = @(x)bitand(x,2.^(0:7))>0;

%         pport.get =@()iofun(pptio);
%         pport.put =@(x)iofun(pptio,dec2logic(x),false);
        pport.get =@()iofun();
        pport.put =@(x)iofun(uint8(dec2logic(x))');
        pport.obj = [];
        
        
end
        

