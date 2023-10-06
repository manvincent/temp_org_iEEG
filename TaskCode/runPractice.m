
function [taskStruct, dispStruct] = runPractice(taskStruct, dispStruct)
    fireEvent(taskStruct.LPT, taskStruct.ePRACTICE_START);
    
    % a few practice trials
    Screen('TextSize', dispStruct.wPtr, 30);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    text1 = 'Before we start, let''s try 5 practice trials\n\n';
    text2 = 'Press any key to begin';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 'center', [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip');
    % wait for key press to continue
    RestrictKeysForKbCheck( [] );
    KbWait(-3, 2);
    Screen(dispStruct.wPtr, 'Flip');
    
    practiceTrialCards = [4 8; 7 2; 1 5; 10 7; 3 1];
    for pI = 1 : size(practiceTrialCards,1)
        % build this trial's structure
        trialStruct = buildTrialStruct(practiceTrialCards(pI, :));
        
        % create a new struct on trial 1, compile thereafter
        if pI == 1
            taskStruct.practiceTrials = runTrial(taskStruct, dispStruct, trialStruct);
        else
            taskStruct.practiceTrials(pI) = runTrial(taskStruct, dispStruct, trialStruct);
        end
        
        % save the data
        save( fullfile(taskStruct.outputFolder, taskStruct.fileName), 'taskStruct', 'dispStruct');
        
        % show the summary
        trialStruct = runSummary(taskStruct, dispStruct, taskStruct.practiceTrials(pI));
        
        % check for quit button
        RestrictKeysForKbCheck( [dispStruct.respKey_Quit, dispStruct.respKey_Pause] );
        [secs, keyCode] = KbWait( -3, 0, GetSecs()+0.10);
        if ismember(find(keyCode, 1),dispStruct.respKey_Quit )
            RestrictKeysForKbCheck( [] );
            Screen('TextSize', dispStruct.wPtr, 30);
            Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
            text1 = 'Do you really want to quit?\n\n';
            [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 'center');
            Screen(dispStruct.wPtr, 'Flip');

            % wait for a second Q press (or any other key to continue) 
            [secs, keyCode] = KbWait( -3, 2);
            if ismember(find(keyCode, 1),dispStruct.respKey_Quit )
                % terminate
                throw(MException(-1, 'user quit'));
            end
        elseif ismember(find(keyCode, 1),dispStruct.respKey_Pause )
            runPause(taskStruct, dispStruct);
        end
    end % for each practice trial
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Practice done!
    Screen('TextSize', dispStruct.wPtr, 30);
    text1 = 'We''re done with the practice.\nPlease let the experimenter know if you have any questions, or if anything is unclear.\n\n';
    text2 = 'Press any key to start the game';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', dispStruct.centerY - 30, [], 70, false, false, 1.1);
    DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip');
    fireEvent(taskStruct.LPT, taskStruct.ePRACTICE_END);
    % wait for key press to continue
    RestrictKeysForKbCheck( KbName('space') );
    KbWait(-3, 2);
    Screen(dispStruct.wPtr, 'Flip');
end