function blkStruct = slblocks

    blkStruct.Name = ['PaPI' sprintf('\n') 'Library'];

    Browser(1).Name = 'PaPI';
    Browser(1).Library = 'PaPI';
    Browser(1).IsFlat  = 0;

    blkStruct.Browser = Browser;
