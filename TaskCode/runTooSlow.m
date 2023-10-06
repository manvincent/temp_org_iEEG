function [] = runTooSlow(taskStruct, dispStruct, trialStruct)
    Screen(dispStruct.wPtr, 'Flip');
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '- Too Slow! -', 'center', 50);
    
    Screen('TextSize', dispStruct.wPtr, 30);
    
    % guess feedback
    text1 = ['You have ' num2str(taskStruct.MAX_RT) ' seconds to make a response.\n\n'];
    text2 = 'Please try to respond faster.\n\n';
    text3 = ['Time penalty of ' num2str(taskStruct.SLOW_AMOUNT) ' points\n\n'];
    text4 = 'Press any key to continue';
    
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text4, 'center', ny);
    Screen(dispStruct.wPtr, 'Flip');
    RestrictKeysForKbCheck( [] );
    KbWait(-3, 2);
end % too slow