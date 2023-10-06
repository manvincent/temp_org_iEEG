function [] = runCardDrawInstructions(taskStruct, dispStruct)
    % initialize the instruction display
    dispStruct = initInstDisplay(dispStruct);
    
    % list of instructions to show
    instructions = 1:15;
    % init the current instruction
    currentInst = 1;

    % loop until done signal
    doneInst = false;
    while ~doneInst
        % run the instruction function
        RestrictKeysForKbCheck([]);
        feval(['Instructions_CardDraw_' num2str(currentInst)], taskStruct, dispStruct);
        
        % wait for navigation input
        RestrictKeysForKbCheck( [dispStruct.instKeyPrev, dispStruct.instKeyNext, dispStruct.instKeyDone, dispStruct.respKey_Quit] );
        [~, keyCode] = KbWait(-3, 2);

        % update the current instructin according to key press
        respKey = find(keyCode);
        if ismember(respKey, dispStruct.instKeyPrev)
            % move back a screen
            currentInst = max(1, currentInst-1);
        elseif ismember(respKey, dispStruct.instKeyNext)
            % move forward
            currentInst = min(length(instructions), currentInst+1);
        elseif respKey == dispStruct.instKeyDone && currentInst == length(instructions)
            doneInst = true;
        elseif respKey ==  dispStruct.respKey_Quit
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
        end
    end
end

function dispStruct = initInstDisplay(dispStruct)
    % keys for navigating the instructions
    dispStruct.instKeyPrevName = 'L';
    dispStruct.instKeyNextName = 'R';
    dispStruct.instKeyPrev = [ KbName('1!'), KbName('1') ];
    dispStruct.instKeyNext = [ KbName('3#'), KbName('3') ];
    dispStruct.instKeyDone = KbName('space');
    
    % card & button rects for basic knowledge test
    scallingFactor = 1.5; cardGap = 200;
    rectCard_width = scallingFactor*73; rectCard_height = scallingFactor*100;
    rectCard_LeftX = dispStruct.centerX - (cardGap/2) - rectCard_width;
    rectCard_TopY = dispStruct.centerY - (rectCard_height/2);
    dispStruct.rectCardBasicTest_Left = [rectCard_LeftX, rectCard_TopY, rectCard_LeftX+rectCard_width, rectCard_TopY+rectCard_height];
    % set up the right card
    dispStruct.rectCardBasicTest_Right = dispStruct.rectCardBasicTest_Left;
    dispStruct.rectCardBasicTest_Right([1 3]) = dispStruct.rectCardBasicTest_Right([1 3]) + rectCard_width + cardGap;
    % set up the labels
    dispStruct.rectCardLabelBasicTest_Left = dispStruct.rectCardBasicTest_Left;
    dispStruct.rectCardLabelBasicTest_Left([2 4]) = [dispStruct.rectCardLabelBasicTest_Left(2)-30, dispStruct.rectCardLabelBasicTest_Left(2)-10];
    dispStruct.rectCardLabelBasicTest_Right = dispStruct.rectCardBasicTest_Right;
    dispStruct.rectCardLabelBasicTest_Right([2 4]) = [dispStruct.rectCardLabelBasicTest_Right(2)-30, dispStruct.rectCardLabelBasicTest_Right(2)-10];
    
    % set up the choices
    rectChoice_width = 150; rectChoice_height = 100; rectChoice_gap = 200;
    rectChoice = [0 0 rectChoice_width rectChoice_height];
    % put left/right choices into position
    rectChoice_LeftX = dispStruct.rectCardBasicTest_Left(1)+(rectCard_width/2) - (rectChoice_width/2);
    rectChoice_TopY = dispStruct.rectCardBasicTest_Left(4) + 40;
    dispStruct.rectChoiceBasicTest_Left = rectChoice + [rectChoice_LeftX, rectChoice_TopY, rectChoice_LeftX, rectChoice_TopY];
    % set up the right choice
    rectChoice_LeftX = dispStruct.rectCardBasicTest_Right(1)+(rectCard_width/2) - (rectChoice_width/2);
    rectChoice_TopY = dispStruct.rectCardBasicTest_Left(4) + 40;
    dispStruct.rectChoiceBasicTest_Right = rectChoice + [rectChoice_LeftX, rectChoice_TopY, rectChoice_LeftX, rectChoice_TopY];
    
end

function [] = Instructions_CardDraw_1(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 1 -', 'center', 50);

    % instruction text
    text1 = 'Thank you very much for participating today.\nWe hope you have fun playing this card game.\nYour goal is to earn as many points as you can.\n\n';
    text2 = 'First we will go through some instructions to make sure you understand the game and can earn as many points as possible\n\n';
    text3 = ['Use the ''' dispStruct.instKeyPrevName ''' (previous) and ''' dispStruct.instKeyNextName ''' (next) buttons\nto navigate through the instructions'];
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);

    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_2(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 2 -', 'center', 50);

    % instruction text
    text1 = 'In this game you will be dealt two cards;\nfirst one, then the second.\n\n';
    text2 = 'You''re job is to guess whether the second card is HIGHER or LOWER than the first\n\n';
    text3 = 'You win 10 points if you guess correctly,\nbut lose 10 points if you guess wrong.\n\n';
    text4 = 'The deck has 10 cards that will be reshuffled before each deal\n(Ace, 2, 3, 4, 5, 6, 7, 8, 9, 10)';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text4, 'center', ny, [], 70, false, false, 1.1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text2 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_3(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 3 -', 'center', 50);

    % instruction text
    text1 = ['Which of these two cards is HIGHER?\nUse the ''' dispStruct.respKeyName_Left ''' to pick the card on the left, or the ''' dispStruct.respKeyName_Right ''' keys to pick the card on the right'];
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    % show the cards
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(5), [], dispStruct.rectCardBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(9), [], dispStruct.rectCardBasicTest_Right);
    % show the labels
    Screen('TextSize', dispStruct.wPtr, 15);
%     DrawFormattedText(dispStruct.wPtr, 'Card1', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Left);
%     DrawFormattedText(dispStruct.wPtr, 'Card2', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Right);
    
    % show the higher/lower options
    % show the high/low choice buttons & wait for response
%     Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectChoiceBasicTest_Left);
%     Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectChoiceBasicTest_Right);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Right );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectCardBasicTest_Right, 5);
    Screen('TextSize', dispStruct.wPtr, 15);
    text2 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_4(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 4 -', 'center', 50);

    % instruction text
    text1 = ['Which of these two cards is LOWER?\nUse the ''' dispStruct.respKeyName_Left ''' to pick the card on the left, or the ''' dispStruct.respKeyName_Right ''' keys to pick the card on the right'];
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    % show the cards
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(1), [], dispStruct.rectCardBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(3), [], dispStruct.rectCardBasicTest_Right);
    % show the labels
%     Screen('TextSize', dispStruct.wPtr, 15);
%     DrawFormattedText(dispStruct.wPtr, 'Card1', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Left);
%     DrawFormattedText(dispStruct.wPtr, 'Card2', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Right);
    
    % show the higher/lower options
    % show the high/low choice buttons & wait for response
%     Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectChoiceBasicTest_Left);
%     Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectChoiceBasicTest_Right);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Left );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('TextSize', dispStruct.wPtr, 15);
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectCardBasicTest_Left, 5);
    text2 = ['In this game, Aces are the lowest card.\nUse the ''' dispStruct.instKeyNextName ''' (next) button\nto continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.rectChoiceBasicTest_Right(4) + 25, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_5(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 5 -', 'center', 50);

    % instruction text
    text1 = ['If you guessed that the 2nd card was HIGHER than the 1st,\nDid you win or lose?\n(use the ''' dispStruct.respKeyName_Left ''' or ''' dispStruct.respKeyName_Right ''' keys to choose your answer)'];
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    % show the cards
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(3), [], dispStruct.rectCardBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(1), [], dispStruct.rectCardBasicTest_Right);
    % show the labels
    Screen('TextSize', dispStruct.wPtr, 15);
    DrawFormattedText(dispStruct.wPtr, '1st', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Left);
    DrawFormattedText(dispStruct.wPtr, '2nd', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Right);
    
    % show the higher/lower options
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Win, [], dispStruct.rectChoiceBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Loss, [], dispStruct.rectChoiceBasicTest_Right);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Right );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('TextSize', dispStruct.wPtr, 15);
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectChoiceBasicTest_Right, 5);
    text2 = ['In this game, Aces are the lowest card.\nUse the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.rectChoiceBasicTest_Right(4) + 25, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_6(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 6 -', 'center', 50);

    % instruction text
    text1 = ['If you guessed that the 2nd card was LOWER than the 1st,\nDid you win or lose?\n(use the ''' dispStruct.respKeyName_Left ''' or ''' dispStruct.respKeyName_Right ''' keys to choose your answer)'];
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    % show the cards
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(8), [], dispStruct.rectCardBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(4), [], dispStruct.rectCardBasicTest_Right);
    % show the labels
    Screen('TextSize', dispStruct.wPtr, 15);
    DrawFormattedText(dispStruct.wPtr, 'Card1', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Left);
    DrawFormattedText(dispStruct.wPtr, 'Card2', 'center', 'center', [], [], [], [], [], [], dispStruct.rectCardLabelBasicTest_Right);
    
    % show the higher/lower options
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Win, [], dispStruct.rectChoiceBasicTest_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Loss, [], dispStruct.rectChoiceBasicTest_Right);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Left );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectChoiceBasicTest_Left, 5);
    Screen('TextSize', dispStruct.wPtr, 15);
    text2 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_7(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 7 -', 'center', 50);

    % instruction text
    text1 = 'After both cards have been dealt, you will be asked to report whether your guess won or lost\n\n';
    text2 = 'If you report accurately you get a bonus 5 points;\nreporting that you won when you guessed correctly,\nor that you lost when you guessed incorrectly\n\n.';
    text3 = 'If you report inaccurately you lose 5 points;\nreporting that you won when you guessed incorrectly,\nor the that you lost when you guessed correctly';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text4 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text4, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_8(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 8 -', 'center', 50);

    % instruction text
    text1 = 'Starting on the next instruction screen, we will show you an example of what the game looks like.';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text4 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text4, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_9(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 9 -', 'center', 50);

    % instruction text
    text1 = 'First, guess whether the 2nd card will be LOWER or HIGHER than the 1st.\nUse the left button to pick LOWER';
    Screen('TextSize', dispStruct.wPtr, 25);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 80, false, false, 1.1);
    
    % show the high/low choice buttons & wait for response
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectButtonGuess_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectButtonGuess_Right);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text2 = 'LOWER and HIGHER can appear on either the left or right.\nThere position is totally random to ensure no advantage for being left or right handed.';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.rectButtonGuess_Right(4) + 150, [], 70, false, false, 1.1);
    
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Left );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % clear the screen & redraw the selected button
    Screen('TextSize', dispStruct.wPtr, 25);
    text3 = 'The cards are shuffled and the first card is dealt';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', 150, [], 70, false, false, 1.1);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectButtonGuess_Left);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show fixation and the first card
    Screen('TextSize', dispStruct.wPtr, 40);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show the first card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(8), [], dispStruct.rectCard);
    Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(4);
    
    % clear the screen & show fixation with the selected button
    Screen(dispStruct.wPtr, 'Flip');
    Screen('TextSize', dispStruct.wPtr, 40);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectButtonGuess_Left);
    Screen('TextSize', dispStruct.wPtr, 25);
    text4 = 'The first card is removed, and the second card is dealt';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text4, 'center', 150, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show the second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(4), [], dispStruct.rectCard);
    Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(5);
    
    % redraw choice and second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectButtonGuess_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(4), [], dispStruct.rectCard);
    
    % show choice
    Screen('TextSize', dispStruct.wPtr, 25);
    text5 = 'Then you will be asked to report whether your guess won or lost.\n\n';
    text6 = 'The 2nd card (4) was LOWER than the 1st card (8), which is what you guessed.\nUse the left button to pick I WON\n\n';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text5, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text6, 'center', ny, [], 70, false, false, 1.1);
    
    % show win/loss buttons
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Win, [], dispStruct.rectButtonReport_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Loss, [], dispStruct.rectButtonReport_Right);
    Screen('TextSize', dispStruct.wPtr, 15);
    text7 = '''I Won'' and ''I Lost'' can appear randomply on either the left or right to ensure no advantage for being left or right handed.\n\n';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text7, 'center', dispStruct.rectButtonReport_Right(4) + 50, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    RestrictKeysForKbCheck( dispStruct.respKey_Left );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectButtonReport_Left, 5);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text4 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    rectTextCover = [dispStruct.wPtrRect(1), dispStruct.rectButtonReport_Right(4) + 50, dispStruct.wPtrRect(3), dispStruct.wPtrRect(4)];
    Screen('FillRect', dispStruct.wPtr, dispStruct.bgColor, rectTextCover);
    DrawFormattedText(dispStruct.wPtr, text4, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_10(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 10 -', 'center', 50);

    % instruction text
    text1 = 'You won 10 points because you guessed that the second card was LOWER.\n';
    text2 = 'The second card (4) was LOWER than the first card (8).\n';
    text3 = 'You also won 5 points because you accurately reported that your guess WON.';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);
    
    % show the guess
    guessWidth = dispStruct.buttonWidth;
    guessHeight = dispStruct.buttonHeight;
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectGuessText = [leftX, topY, leftX+guessWidth, topY+20];
    rectGuess = [leftX, rectGuessText(4)+10, leftX+guessWidth, rectGuessText(4)+10+guessHeight];
    rectGuessPoints = [rectGuessText(1), rectGuess(4)+10, rectGuessText(3), rectGuess(4)+30];
    
    % show the high/low choice buttons & wait for response
    DrawFormattedText(dispStruct.wPtr, 'Guess', 'center', 'center', [],[],[],[],[],[], rectGuessText);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], rectGuess);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '10 Points', 'center', 'center', [],[],[],[],[],[], rectGuessPoints);
    
    % show the report
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectReportText = [leftX, topY, leftX+guessWidth, topY+20];
    rectReport = [leftX, rectReportText(4)+10, leftX+guessWidth, rectReportText(4)+10+guessHeight];
    rectReportPoints = [rectReportText(1), rectReport(4)+10, rectReportText(3), rectReport(4)+30];
    % show the high/low choice buttons & wait for response
    DrawFormattedText(dispStruct.wPtr, 'Report', 'center', 'center', [],[],[],[],[],[], rectReportText);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Win, [], rectReport);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '5 Points', 'center', 'center', [],[],[],[],[],[], rectReportPoints);
    
    % show the total
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectTotalText = [leftX, topY, leftX+guessWidth, topY+20];
    DrawFormattedText(dispStruct.wPtr, 'Total\n15 Points', 'center', 'center', [],[],[],[],[],[], rectTotalText);
    text8 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    Screen('TextSize', dispStruct.wPtr, 15);
    DrawFormattedText(dispStruct.wPtr, text8, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_11(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 11 -', 'center', 50);

    % instruction text
    text1 = 'Let''s try another example.\nStarting on the next instruction screen, we will show you a second example deal.';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text8 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text8, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_12(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 12 -', 'center', 50);
    
    
     % instruction text
    text1 = 'First, guess whether the second card will be LOWER or HIGHER than the first.\nUse the left button to pick HIGHER';
    Screen('TextSize', dispStruct.wPtr, 25);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 80, false, false, 1.1);
    
    % show the high/low choice buttons & wait for response
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectButtonGuess_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Lower, [], dispStruct.rectButtonGuess_Right);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text2 = 'LOWER and HIGHER can appear on either the left or right.\nThere position is totally random to ensure no advantage for being left or right handed.';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', dispStruct.rectButtonGuess_Right(4) + 150, [], 70, false, false, 1.1);
    
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
    
    % wait for response
    RestrictKeysForKbCheck( dispStruct.respKey_Left );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % clear the screen & redraw the selected button
    Screen('TextSize', dispStruct.wPtr, 25);
    text3 = 'The cards are shuffled and the first card is dealt';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', 150, [], 70, false, false, 1.1);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectButtonGuess_Left);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show fixation and the first card
    Screen('TextSize', dispStruct.wPtr, 40);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show the first card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(7), [], dispStruct.rectCard);
    Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(4);
    
    
    % clear the screen & show fixation with the selected button
    Screen(dispStruct.wPtr, 'Flip');
    Screen('TextSize', dispStruct.wPtr, 40);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectButtonGuess_Left);
    Screen('TextSize', dispStruct.wPtr, 25);
    text4 = 'The first card is removed, and the second card is dealt';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text4, 'center', 150, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    WaitSecs(1);
    
    % show the second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(1), [], dispStruct.rectCard);
    Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(5);
    
    % redraw choice and second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], dispStruct.rectButtonGuess_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(1), [], dispStruct.rectCard);
    
    % show choice
    Screen('TextSize', dispStruct.wPtr, 25);
    text5 = 'Then you will be asked to report whether your guess won or lost.\n\n';
    text6 = 'Use the left button to pick I LOST\n(the second card was LOWER than the first)\n\n';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text5, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text6, 'center', ny, [], 70, false, false, 1.1);
    
    % show win/loss buttons
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Win, [], dispStruct.rectButtonReport_Left);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Loss, [], dispStruct.rectButtonReport_Right);
    Screen('TextSize', dispStruct.wPtr, 15);
    text7 = '''I Won'' and ''I Lost'' can appear randomply on either the left or right to ensure no advantage for being left or right handed.\n\n';
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text7, 'center', dispStruct.rectButtonReport_Right(4) + 50, [], 70, false, false, 1.1);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    RestrictKeysForKbCheck( dispStruct.respKey_Right );
    KbWait(-3, 2);
    RestrictKeysForKbCheck( [] );
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], dispStruct.rectButtonReport_Right, 5);
    Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text4 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    rectTextCover = [dispStruct.wPtrRect(1), dispStruct.rectButtonReport_Right(4) + 50, dispStruct.wPtrRect(3), dispStruct.wPtrRect(4)];
    Screen('FillRect', dispStruct.wPtr, dispStruct.bgColor, rectTextCover);
    DrawFormattedText(dispStruct.wPtr, text4, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_13(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 13 -', 'center', 50);

    % instruction text
    text1 = 'You lost 10 points because you guessed that the second card was HIGHER.\n';
    text2 = 'But, the second card (Ace) was LOWER than the first card (7).\n';
    text3 = 'but, you won 5 points because you accurately reported that your guess LOST.';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 80, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 80, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 80, false, false, 1.1);
    
    % show the guess
    guessWidth = dispStruct.buttonWidth;
    guessHeight = dispStruct.buttonHeight;
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectGuessText = [leftX, topY, leftX+guessWidth, topY+20];
    rectGuess = [leftX, rectGuessText(4)+10, leftX+guessWidth, rectGuessText(4)+10+guessHeight];
    rectGuessPoints = [rectGuessText(1), rectGuess(4)+10, rectGuessText(3), rectGuess(4)+30];
    
    % show the high/low choice buttons & wait for response
    DrawFormattedText(dispStruct.wPtr, 'Guess', 'center', 'center', [],[],[],[],[],[], rectGuessText);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgGuess_Higher, [], rectGuess);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '-10 Points', 'center', 'center', [],[],[],[],[],[], rectGuessPoints);
    
    % show the report
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectReportText = [leftX, topY, leftX+guessWidth, topY+20];
    rectReport = [leftX, rectReportText(4)+10, leftX+guessWidth, rectReportText(4)+10+guessHeight];
    rectReportPoints = [rectReportText(1), rectReport(4)+10, rectReportText(3), rectReport(4)+30];
    % show the high/low choice buttons & wait for response
    DrawFormattedText(dispStruct.wPtr, 'Report', 'center', 'center', [],[],[],[],[],[], rectReportText);
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgReport_Loss, [], rectReport);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '5 Points', 'center', 'center', [],[],[],[],[],[], rectReportPoints);
    
    % show the total
    leftX = dispStruct.centerX - (guessWidth/2);
    topY = ny + 50;
    rectTotalText = [leftX, topY, leftX+guessWidth, topY+20];
    DrawFormattedText(dispStruct.wPtr, 'Total\n-5 Points', 'center', 'center', [],[],[],[],[],[], rectTotalText);
    
    Screen('TextSize', dispStruct.wPtr, 15);
    text8 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text8, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    
    
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_14(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 14 -', 'center', 50);

    % instruction text
    text1 = 'Remember, you get 10 points for guessing whether the second card is higher or lower than the first.\n\n';
    text2 = 'But you can also earn a bonus 5 points if you accurately report whether your guess was correct or not.\nUnfortunately, you''ll lose 5 points if you report incorrectly. So, it''s important to pay attention to weather each guess is wins or loses if you want to earn as many points as you can.';
    
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
    
    % show instructions
    Screen('TextSize', dispStruct.wPtr, 15);
    text4 = ['Use the ''' dispStruct.instKeyNextName ''' (next) button to continue with the instructions'];
    DrawFormattedText(dispStruct.wPtr, text4, 'center', dispStruct.wPtrRect(4) - 40, [], 70, false, false, 1.1); 
    Screen(dispStruct.wPtr, 'Flip');
end

function [] = Instructions_CardDraw_15(taskStruct, dispStruct)
    % instruction #
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '- Instructions 15 -', 'center', 50);

    % instruction text
    text1 = 'These are the scores of the top 5 players.';
    Screen('TextSize', dispStruct.wPtr, 15);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 150, [], 70, false, false, 1.1);
    
    leader_Width = 0.8*525;
    leader_Height = 0.8*369;
    leaderX = dispStruct.centerX - round(leader_Width/2);
    leaderY = ny + 50;
    leaderRect = [leaderX, leaderY, leaderX+leader_Width, leaderY+leader_Height];
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.leaderBoard, [], leaderRect);
    
    text2 = 'Do the best you can to get your name on the board, and please ask the experimenter any questions you might have.\n\n';
    text3 = 'Otherwise, let the experimenter know that yor''re ready to begin playing.';
    
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', leaderRect(4)+40, [], 70, false, false, 1.1);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, text3, 'center', ny, [], 70, false, false, 1.1);
    
    % show instructions
    Screen(dispStruct.wPtr, 'Flip');
end





    
    