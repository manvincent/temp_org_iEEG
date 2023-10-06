function eventCode = fireEvent(structLPT, eventCode)
    structLPT.put(0); 
%     disp(0);
    tic, while toc < 0.1;end
    structLPT.put(eventCode);
%     disp(eventCode);
    while toc < 0.1;end
end