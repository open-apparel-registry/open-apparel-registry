import React, { Component } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link, Switch, Route } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';

import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import FacilityListItemsEmpty from './FacilityListItemsEmpty';
import FacilityListItemsTable from './FacilityListItemsTable';

import {
    fetchFacilityList,
    fetchFacilityListItems,
    resetFacilityListItems,
    assembleAndDownloadFacilityListCSV,
} from '../actions/facilityListDetails';

import {
    listsRoute,
    facilityListItemsRoute,
    aboutProcessingRoute,
} from '../util/constants';

import { facilityListPropType } from '../util/propTypes';

import { createPaginationOptionsFromQueryString } from '../util/util';

const facilityListItemsStyles = Object.freeze({
    headerStyles: Object.freeze({
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0.5rem',
        marginBottom: '0.5rem',
        marginTop: '60px',
        alignContent: 'center',
        alignItems: 'center',
    }),
    subheadStyles: Object.freeze({
        padding: '0.5rem',
        textAlign: 'left',
    }),
    tableStyles: Object.freeze({
        minWidth: '85%',
        width: '90%',
    }),
    tableTitleStyles: Object.freeze({
        fontFamily: 'ff-tisa-sans-web-pro, sans-serif',
        fontWeight: 'normal',
        fontSize: '32px',
    }),
    descriptionStyles: Object.freeze({
        marginBottm: '30px',
    }),
    buttonStyles: Object.freeze({
        marginLeft: '20px',
    }),
    buttonGroupStyles: Object.freeze({
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    }),
    buttonGroupWithErrorStyles: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignContent: 'center',
    }),
});

class FacilityListItems extends Component {
    componentDidMount() {
        this.props.fetchList();
        this.props.fetchListItems();
    }

    componentWillUnmount() {
        return this.props.clearListItems();
    }

    render() {
        const {
            list,
            fetchingList,
            error,
            downloadCSV,
            downloadingCSV,
            csvDownloadingError,
        } = this.props;

        if (fetchingList) {
            return (
                <AppGrid title="">
                    <CircularProgress />
                </AppGrid>
            );
        }

        if (error && error.length) {
            return (
                <AppGrid title="Unable to retrieve that list">
                    <ul>
                        {
                            error
                                .map(err => (
                                    <li key={err}>
                                        {err}
                                    </li>))
                        }
                    </ul>
                </AppGrid>
            );
        }

        if (!list) {
            return (
                <AppGrid title="No list was found for that ID">
                    <div />
                </AppGrid>
            );
        }

        const csvDownloadErrorMessage = (csvDownloadingError && csvDownloadingError.length)
            ? (
                <p style={{ color: 'red', textAlign: 'right' }}>
                    An error prevented downloading the CSV.
                </p>)
            : null;

        const csvDownloadButton = downloadingCSV
            ? (
                <div>
                    <CircularProgress size={25} />
                </div>)
            : (
                <Button
                    variant="outlined"
                    color="primary"
                    style={facilityListItemsStyles.buttonStyles}
                    onClick={downloadCSV}
                    disabled={downloadingCSV}
                >
                    Download CSV
                </Button>);

        return (
            <AppOverflow>
                <Grid
                    container
                    justify="center"
                >
                    <Grid
                        item
                        style={facilityListItemsStyles.tableStyles}
                    >
                        <div style={facilityListItemsStyles.headerStyles}>
                            <div>
                                <h2 style={facilityListItemsStyles.titleStyles}>
                                    {list.name || list.id}
                                </h2>
                                <Typography
                                    variant="subheading"
                                    style={facilityListItemsStyles.descriptionStyles}
                                >
                                    {list.description || ''}
                                </Typography>
                            </div>
                            <div style={facilityListItemsStyles.buttonGroupWithErrorStyles}>
                                {csvDownloadErrorMessage}
                                <div style={facilityListItemsStyles.buttonGroupStyles}>

                                    {csvDownloadButton}
                                    <Button
                                        variant="outlined"
                                        component={Link}
                                        to={listsRoute}
                                        href={listsRoute}
                                        style={facilityListItemsStyles.buttonStyles}
                                    >
                                        Back to lists
                                    </Button>
                                </div>
                            </div>
                        </div>
                        <div style={facilityListItemsStyles.subheadStyles}>
                            Read about how your facility lists are processed and
                            matched in this&nbsp;
                            <Link to={aboutProcessingRoute} href={aboutProcessingRoute}>guide</Link>
                        </div>
                        {
                            list.item_count
                                ? (
                                    <Switch>
                                        <Route
                                            path={facilityListItemsRoute}
                                            component={FacilityListItemsTable}
                                        />
                                    </Switch>)
                                : <FacilityListItemsEmpty />
                        }
                    </Grid>
                </Grid>
            </AppOverflow>
        );
    }
}

FacilityListItems.defaultProps = {
    list: null,
    error: null,
    csvDownloadingError: null,
};

FacilityListItems.propTypes = {
    list: facilityListPropType,
    fetchingList: bool.isRequired,
    error: arrayOf(string),
    fetchList: func.isRequired,
    fetchListItems: func.isRequired,
    clearListItems: func.isRequired,
    downloadCSV: func.isRequired,
    downloadingCSV: bool.isRequired,
    csvDownloadingError: arrayOf(string),
};

function mapStateToProps({
    facilityListDetails: {
        list: {
            data: list,
            fetching: fetchingList,
            error: listError,
        },
        items: {
            error: itemsError,
        },
        downloadCSV: {
            fetching: downloadingCSV,
            error: csvDownloadingError,
        },
    },
}) {
    return {
        list,
        fetchingList,
        error: listError || itemsError,
        downloadingCSV,
        csvDownloadingError,
    };
}

function mapDispatchToProps(dispatch, {
    match: {
        params: {
            listID,
        },
    },
    history: {
        location: {
            search,
        },
    },
}) {
    const {
        page,
        rowsPerPage,
    } = createPaginationOptionsFromQueryString(search);

    return {
        fetchList: () => dispatch(fetchFacilityList(listID)),
        fetchListItems: () => dispatch(fetchFacilityListItems(listID, page, rowsPerPage)),
        clearListItems: () => dispatch(resetFacilityListItems()),
        downloadCSV: () => dispatch(assembleAndDownloadFacilityListCSV()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(FacilityListItems);
