function [] = runPause(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Pause -', 'center', 50);

    
    text1 = ['So far you''ve played ' num2str(taskStruct.trialTotal) ' times\n'];
    text2 = ['And so far you''ve earned ' num2str(taskStruct.totalEarnings) ' points\n\n'];
    text3 = 'Press key when you''re ready to continue\n\n';

    Screen('TextSize', dispStruct.wPtr, 30);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);
    
    
    text1 = 'Top 5.';
    Screen('TextSize', dispStruct.wPtr, 20);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', ny, [], 70, false, false, 1.1);
    leader_Width = 0.7*525;
    leader_Height = 0.7*369;
    leaderX = dispStruct.centerX - round(leader_Width/2);
    leaderY = ny + 50;
    leaderRect = [leaderX, leaderY, leaderX+leader_Width, leaderY+leader_Height];
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.leaderBoard, [], leaderRect);
    
    
    Screen(dispStruct.wPtr, 'Flip');
    
    RestrictKeysForKbCheck( dispStruct.respKey_Pause );
    KbWait(-3, 2);
end