/* Measure on layout changes only. Scroll animation remains entirely in CSS. */
(() => {
    const ending = document.querySelector('.project-ending');
    const process = ending?.querySelector('.project-process');
    if (!process || !ending.querySelector('.project-closing-sheet')) return;
    const header = document.querySelector('.site-header');
    const chapter = process.querySelector('.project-process__chapter');
    const copy = process.querySelector('.project-process__copy');
    const media = process.querySelector('.project-process__media');
    const px = value => Number.parseFloat(value) || 0;
    const outerHeight = element => {
        if (!element) return 0;
        const style = getComputedStyle(element);
        return element.getBoundingClientRect().height + px(style.marginBlockStart) + px(style.marginBlockEnd);
    };
    let frame = 0;
    const measure = () => {
        frame = 0;
        const style = getComputedStyle(process);
        const imageStyle = media && getComputedStyle(media);
        const ratioParts = imageStyle?.aspectRatio.split('/').map(px);
        const ratio = ratioParts?.length === 2 ? ratioParts[0] / ratioParts[1] : 0;
        const imageFloor = imageStyle ? Math.max(px(imageStyle.minBlockSize), ratio ? media.getBoundingClientRect().width / ratio : 0)
            + px(imageStyle.marginBlockStart) + px(imageStyle.marginBlockEnd) : 0;
        const minimum = Math.ceil(px(style.paddingBlockStart) + px(style.paddingBlockEnd)
            + outerHeight(chapter) + px(style.rowGap) + Math.max(outerHeight(copy), imageFloor));
        const value = `${minimum}px`;
        if (ending.style.getPropertyValue('--process-content-min') !== value)
            ending.style.setProperty('--process-content-min', value);
        if (header) {
            const height = `${header.getBoundingClientRect().height}px`;
            if (ending.style.getPropertyValue('--site-header-height') !== height)
                ending.style.setProperty('--site-header-height', height);
        }
        ending.dataset.motionReady = '';
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(measure); };
    const observer = new ResizeObserver(schedule);
    [chapter, copy, header].filter(Boolean).forEach(element => observer.observe(element));
    window.addEventListener('resize', schedule, { passive: true });
    window.addEventListener('pageshow', schedule);
    document.fonts.ready.then(schedule);
    measure();
})();
