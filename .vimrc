"http://www.thegeekstuff.com/2008/12/vi-and-vim-autocommand-3-steps-to-add-custom-header-to-your-file/
autocmd bufnewfile *.py so ./py_header.txt
autocmd bufnewfile *.py exe "1," . 10 . "g/Creation Date :.*/s//Creation Date : " .strftime("%d-%m-%Y")
autocmd bufnewfile *.py exe "1," . 10 . "g/Author :.*/s//Author : "  $USER
autocmd Bufwritepre,filewritepre *.py execute "normal ma"
autocmd Bufwritepre,filewritepre *.py exe "1," . 10 . "g/Last Modified :.*/s/Last Modified :.*/Last Modified : " .strftime("%c")
autocmd bufwritepost,filewritepost *.py execute "normal `a"

let g:ultisnips_python_style="sphinx"
